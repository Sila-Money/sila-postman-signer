"""Handles custom 'private-key' authorization header parsing and signature generation."""

import logging

from . import keys

logger = logging.getLogger(__name__)


class AuthorizationError(Exception):
    """To be thrown when an unsupported authorization method is sent."""

class ParseAuthorizationHeaderError(Exception):
    """To be thrown when header cannot be parsed."""


def get_signature_headers(authorization_header: str, request_body: str) -> dict:
    """
    Gets private keys from authorization header, generates signatures
    using the request body, and returns those signatures in a dict.
    """
    pk_headers = {}
    signature_headers = {}

    if authorization_header:
        try:
            pk_headers = parse_private_key_authorization_header(authorization_header)
        except Exception as exc:
            logger.error("Invalid Authorization header:", str(exc))

    for pk_header in pk_headers:
        key = pk_headers[pk_header]
        if not keys.is_valid_private_key(key):
            logger.error('The key provided to generate the %s header is not a valid private key.', pk_header)
            continue
        signature_headers[pk_header] = keys.sign_message(request_body.encode('utf-8'), key)
    return signature_headers


def parse_private_key_authorization_header(authorization_header: str, ignore_parse_errors=False):
    """
    Only allows "private-key" authorization.
    Returns a dictionary of desired headers to private keys used to generate the headers.

    If ignore_parse_errors is True, ignores any problematic header arguments
    and just returns a dictionary of all parsed headers arguments.
    If False, 
    """
    requested_signature_headers_dict = {}

    raw_header_args = authorization_header.split(';')
    if raw_header_args[0].lower().strip() != "private-key":
        raise AuthorizationError(f"Unsupported Authorization method: {raw_header_args[0]}")

    for raw_arg in raw_header_args:
        kv_arg_set = raw_arg.strip().split('=')
        if len(kv_arg_set) < 2:
            if ignore_parse_errors or raw_arg == raw_header_args[0]:
                continue
            raise ParseAuthorizationHeaderError(f"Could not parse header argument: {raw_arg.strip()}")
        requested_signature_headers_dict[kv_arg_set[0].strip()] = kv_arg_set[1].strip()

    return requested_signature_headers_dict
