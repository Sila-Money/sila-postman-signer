"""Handles custom 'private-key' authorization header parsing."""

import logging

from . import ethkeys

logger = logging.getLogger(__name__)


class AuthorizationError(Exception):
    """To be thrown when an unsupported authorization method is sent."""

class ParseAuthorizationHeaderError(Exception):
    """To be thrown when header cannot be parsed."""


def get_signature_headers(request_headers, request_body):
    authsignature = request_headers.get('authsignature')
    usersignature = request_headers.get("usersignature")
    auth_pk = request_headers.get('x-auth-private-key')
    user_pk = request_headers.get('x-user-private-key')
    authorization = request_headers.get('authorization')

    pk_headers = {}
    signature_headers = {}

    if authsignature:
        signature_headers["authsignature"] = authsignature
    if usersignature:
        signature_headers["usersignature"] = usersignature

    if authorization:
        try:
            pk_headers = parse_private_key_authorization_header(authorization)
        except Exception as exc:
            logger.error("Invalid Authorization header:", str(exc))
    else:
        if auth_pk:
            pk_headers["authsignature"] = auth_pk
        if user_pk:
            pk_headers["usersignature"] = user_pk

    for pk_header in pk_headers:
        key = pk_headers[pk_header]
        try:
            ethkeys.get_private_key_address(key)
        except Exception as exc:
            logger.error("Invalid private key:", str(exc))
            continue

        signature_headers[pk_header] = ethkeys.sign_message(request_body.encode('utf-8'), key)
    return signature_headers


def parse_private_key_authorization_header(authorization_header_value, ignore_parse_errors=False):
    """
    Only allows "private-key" authorization.
    Returns a dictionary of desired headers to private keys used to generate the headers.
    If ignore_parse_errors is True, ignores any problematic header arguments
    and returns a dictionary of all parsed headers arguments.
    """
    requested_signature_headers_dict = {}

    raw_header_args = authorization_header_value.split(';')
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
