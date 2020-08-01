"""
Endpoints served by Flask to sign, modify, and forward requests to desired targets.
Intended for use on localhost only.

Designed for use with the Sila API (https://www.silamoney.com) and Postman.
"""

import json
import logging
import uuid
from datetime import datetime

import requests
from flask import Flask, request

from . import keys, auth, request_transform

logger = logging.getLogger(__name__)
app = Flask(__name__)


@app.route('/', methods=['OPTIONS', 'GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def root():
    return forward()


@app.route('/generate_private_key', methods= ['OPTIONS', 'GET', 'POST'])
def generate_private_key():
    """
    Generates a private key, public address, and wallet verification signature
    that can be used to register a second wallet.

    Use of the private key generated at this endpoint cannot be considered secure
    if this endpoint has been exposed to a public network.

    This is a convenience method and is not recommended for applications other than
    tests on the sandbox API.
    """
    private_key = keys.generate_private_key()
    address = keys.get_private_key_address(private_key)
    return {
        "private_key": private_key,
        "address": address,
        "wallet_verification_signature": keys.sign_message(address.encode('utf-8'), private_key),
    }


@app.route('/forward', methods=['OPTIONS', 'GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def forward():
    """
    Forwards requests to desired host.

    Generates signature headers and optionally modifies the request body before
    signing with timestamps and UUIDs in requested JSON fields.
    When forwarding request, does not include Authorization header.

    Headers:
    - x-forward-to-url: header to specify full URL to send transformed request.
    - x-set-epoch: header to specify a key in a JSON body to set an epoch timestamp.
    - x-set-uuid: header to specify a key in a JSON body to set a generated UUID4 string.
    - authorization: header to specify private keys to use to sign.
        
        Your private keys can allow access to very sensitive information,
        so if that's the case, please do not host this server anywhere public
        and use common sense to prevent exposure of your secure keys to any public network.
        This functionality is intended for sandbox testing convenience only.
        
        Format of header value should look like:
            'private-key; [desired header name]=[private key]; [another desired header name]=[another private key]'
        For example,
            Authorization: private-key; authsignature=badba7368134dcd61c60f9b56979c09196d03f5891a20c1557b1afac0202a97c

    Query parameters:
    - debug: instead of returning the response as received by the forwarded host,
        returns JSON with the original request body, the request body that was sent, the forwarded
        URL, the generated signature headers, and the response body, headers, and status code.
    """
    SET_EPOCH_HEADER = 'x-set-epoch'
    SET_UUID_HEADER = 'x-set-uuid'
    FORWARD_TO_URL_HEADER = 'x-forward-to-url'

    is_debug = request.args.get("debug")
    set_epoch = request.headers.get(SET_EPOCH_HEADER)
    set_uuid = request.headers.get(SET_UUID_HEADER)
    target_url = request.headers.get(FORWARD_TO_URL_HEADER)

    original_request_body = request.data.decode('utf-8')
    request_body = request_transform.modify_json_request_body(original_request_body, set_epoch, set_uuid)
    
    # Generate signature headers if a valid Authorization header is present.
    # Scrub out headers in scrub list before forwarding request.
    signature_headers = auth.get_signature_headers(request.headers.get('authorization'), request_body)
    scrubbed_request_headers = request_transform.get_scrubbed_request_headers(
        dict(request.headers),
        scrub_list=['authorization', 'host', 'content-length', SET_UUID_HEADER, SET_EPOCH_HEADER, FORWARD_TO_URL_HEADER]
    )
    forwarded_request_headers = {**signature_headers, **scrubbed_request_headers}

    proxy_response_dict = {
        "original_request_body": original_request_body,
        "request_body": request_body,
        "request_headers": forwarded_request_headers,
        "forwarded_to_url": target_url,
    }

    if not target_url:
        proxy_response_dict["message"] = f"No forwarding URL in header {FORWARD_TO_URL_HEADER}, so did not forward request."
    else:
        response = requests.request(
            method=request.method,
            url=target_url,
            data=request_body,
            headers=forwarded_request_headers,
        )
        proxy_response_dict["response"] = {
            "status_code": response.status_code,
            "content": response.content.decode('utf-8'),
            "headers": dict(response.headers),
        }
        try:
            proxy_response_dict["response"]['json_content'] = response.json()
        except Exception as exc:
            logger.error(str(exc))

    if is_debug or 'response' not in proxy_response_dict:
        return proxy_response_dict

    return (
        proxy_response_dict["response"]["content"],
        proxy_response_dict["response"]["status_code"],
        {
            "Forwarded": f"url={target_url}",
            **proxy_response_dict["response"]["headers"]
        }
    )

@app.errorhandler(404)
def endpoint_not_found(e):
    return exception_message_handler(e, message="That resource doesn't exist, sorry!", status=404)


@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, json.decoder.JSONDecodeError):
        return exception_message_handler(e, message=f"Invalid JSON: {e}", status=400)
    return exception_message_handler(e)


def exception_message_handler(e, message=None, status=500):
    if message is None:
        message = str(e)
    return {"success": False, "message": f"Proxy error: {message}"}, status
