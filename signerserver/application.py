"""
Endpoints served by Flask to sign, modify, and forward requests to desired targets.
Intended for use on localhost only.

Designed for use with the Sila API (https://www.silamoney.com).
"""

import json
import logging
import uuid
from datetime import datetime

import requests
from flask import Flask, request

from .common import ethkeys, pkauthorization

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
    private_key = ethkeys.generate_private_key()
    address = ethkeys.get_private_key_address(private_key)
    return {
        "private_key": private_key,
        "address": address,
        "wallet_verification_signature": ethkeys.sign_message(address.encode('utf-8'), private_key),
    }


@app.route('/forward', methods=['OPTIONS', 'GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def forward():
    """
    Forwards requests to desired host.
    Generates signature headers and optionally modifies the request body before
    signing with timestamps and UUIDs in requested JSON fields.
    """
    SET_EPOCH_HEADER = 'x-set-epoch'
    SET_UUID_HEADER = 'x-set-uuid'
    FORWARD_TO_URL_HEADER = 'x-forward-to-url'

    is_debug = request.args.get("debug")
    set_epoch = request.headers.get(SET_EPOCH_HEADER)
    set_uuid = request.headers.get(SET_UUID_HEADER)
    target_url = request.headers.get(FORWARD_TO_URL_HEADER)

    original_request_body = request.data.decode('utf-8')
    request_body = original_request_body
    json_dict = None

    # Check if valid JSON request
    try:
        json_dict = json.loads(original_request_body)
    except Exception as exc:
        return (
            {
                "success": False,
                "message": f"Proxy error: Unable to parse response as JSON: {str(exc)}"
            },
            400
        )

    # Set epoch if in request header
    if set_epoch:
        try:
            set_current_epoch_in_dict(json_dict, str(set_epoch).lower().split("."))
        except Exception as exc:
            return (
                {
                    "success": False,
                    "message": f"Proxy error: Could not set epoch in request body: {str(exc)}"
                },
                400
            )

    # Set epoch if in request header
    if set_uuid:
        try:
            set_value_in_dict(json_dict, str(set_uuid).lower().split("."), str(uuid.uuid4()))
        except Exception as exc:
            return (
                {
                    "success": False,
                    "message": f"Proxy error: Could not set epoch in request body: {str(exc)}"
                },
                400
            )

    request_body = json.dumps(json_dict)
    signature_headers = pkauthorization.get_signature_headers(request.headers, request_body)

    proxy_response_dict = {
        "original_request_body": original_request_body,
        "request_body": request_body,
        "signature_headers": signature_headers,
        "forwarded_to_url": target_url,
    }

    if target_url:
        response = requests.request(
            method=request.method,
            url=target_url,
            data=request_body,
            headers={**signature_headers},
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
    else:
        proxy_response_dict["message"] = "No forwarding URL in header {}, so did not forward request.".format(FORWARD_TO_URL_HEADER)
        
    if is_debug or 'response' not in proxy_response_dict:
        return proxy_response_dict

    return (
        proxy_response_dict["response"]["content"],
        proxy_response_dict["response"]["status_code"],
        {
            "FORWARDED": f"url={target_url}",
            **proxy_response_dict["response"]["headers"]
        }
    )

### Helper functions ###

def set_current_epoch_in_dict(target_dict: dict, keys: list):
    """
    Sets an integer timestamp on a key in target_dict.
    Accepts keys as a tuple and descends into a nested structure in target.
    No return value - the target_dict value will be mutated as a side effect.
    Example: if keys = ("grandparent", "parent", "timestamp"), target_dict
    will contain:
    {
        "grandparent": {
            "parent": {
                "timestamp": <timestamp>
            }
        }
    }
    """
    timestamp = int(datetime.now().timestamp())
    set_value_in_dict(target_dict, keys, timestamp)


def set_value_in_dict(target_dict, keys, value):
    """
    Sets a value on a key in target_dict.
    Accepts keys as a tuple and descends into a nested structure in target.
    No return value - the target_dict value will be mutated as a side effect.
    Example: if keys = ("grandparent", "parent", "timestamp"), target_dict
    will contain:
    {
        "grandparent": {
            "parent": {
                "timestamp": value
            }
        }
    }
    """
    dic = target_dict
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = value
