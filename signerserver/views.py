""" Simple views for simple logic.
    Includes catchalls for 404s and 500s.
"""

import json
import logging

import requests
from django.utils import timezone as django_time

from signerserver.common import ethkeys, pkauthorization
from signerserver.common.response import create_json_response

logger = logging.getLogger(__name__)


def generate_private_key_view(request, *args, **kwargs):
    """ Generates a private key and returns
        the hex string and address.
    """
    private_key = ethkeys.generate_private_key()
    address = ethkeys.get_private_key_address(private_key)
    return create_json_response(
        {
            "private_key": private_key,
            "address": address
        },
        status=200
    )


def generate_signature_view(request, *args, **kwargs):
    """ Looks for X-PRIVATE-KEY header and signs
        the request body with it, then returns
        the signature.
    """
    private_key = request.headers.get('x-private-key')
    if private_key is None:
        return create_json_response(
            {"message": "Bad request: No X-PRIVATE-KEY header found"},
            status=400
        )
    request_body = request.body
    signature = ethkeys.sign_message(request_body, private_key)
    return create_json_response(
        {
            "signature": signature,
            "raw_message": request_body.decode('utf-8')
        },
        status=200
    )


def current_epoch_view(request, *args, **kwargs):
    """ Returns current epoch timestamp data. """
    requested_timezone = request.GET.get("timezone", default="UTC")
    try:
        timezone = django_time.pytz.timezone(requested_timezone)
        now = django_time.now().astimezone(timezone)
        return create_json_response(
            {
                "now_epoch_secs": int(now.timestamp()),
                "now_epoch_millisecs": int(now.timestamp() * 1000),
                "now_iso": now.isoformat(),
                "timezone": requested_timezone,
            }
        )
    except django_time.pytz.UnknownTimeZoneError as exc:
        return create_json_response(
            {
                "message": f"Unknown timezone: {requested_timezone}",
                "accepted_timezones": django_time.pytz.all_timezones
            },
            status=400,
        )


def forwarder_view(request, *args, **kwargs):
    """ Forwards requests to desired host.
        Generates AUTHSIGNATURE and USERSIGNATURE headers
        if X-AUTH-PRIVATE-KEY and X-USER-PRIVATE-KEY are set, respectively.
    """
    original_request_body = request.body.decode('utf-8')
    request_body = original_request_body

    # Set epoch if in request header
    set_epoch = request.headers.get('x-set-epoch')
    if set_epoch:
        try:
            json_dict = json.loads(original_request_body)
            if type(json_dict.get("header")) == dict:
                json_dict["header"]["created"] = int(django_time.now().timestamp())
            request_body = json.dumps(json_dict)
        except Exception as exc:
            return create_json_response(
                {
                    "message": f"Could not parse request body as JSON to set epoch: {str(exc)}"
                },
                status=400,
            )

    signature_headers = pkauthorization.get_signature_headers(request.headers, request_body)
    target_url = request.headers.get('x-forward-to-url')
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
        proxy_response_dict["message"] = "No forwarding URL in header X-FORWARD-TO-URL, so did not forward request."
        
    return create_json_response(proxy_response_dict)


def handler404(request, exception):
    """ Default 404 handler. """
    return create_json_response(
        {"message": "Not found (signerserver error)"},
        status=404
    )


def handler500(request):
    """ Default 500 handler. """
    return create_json_response(
        {"message": "Oh dear! Something borked :( (signerserver error)"},
        status=500
    )
