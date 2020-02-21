""" Simple views for simple logic.
    Includes catchalls for 404s and 500s.
"""

import json

from django.http import HttpResponse

from signerserver.common import ethkeys


def handler404(request, exception):
    ''' Default 404 handler. '''
    return HttpResponse(
        json.dumps({
            "success": False,
            "message": "Not found (signerserver error)",
        }),
        content_type="application/json",
        status=404
    )


def handler500(request):
    ''' Default 500 handler. '''
    return HttpResponse(
        json.dumps({
            "success": False,
            "message": "Oh dear! Something borked :( (signerserver error)"
        }),
        content_type="application/json",
        status=500
    )


def generate_private_key_view(request, *args, **kwargs):
    ''' Generates a private key and returns
        the hex string and address.
    '''
    private_key = ethkeys.generate_private_key()
    address = ethkeys.get_private_key_address(private_key)
    return HttpResponse(
        json.dumps({
            "success": True,
            "private_key": private_key,
            "address": address
        }),
        content_type="application/json",
        status=200
    )


def generate_signature_view(request, *args, **kwargs):
    ''' Looks for a PRIVATEKEY header and signs
        the response body with it, then returns
        the signature.
    '''
    private_key = request.headers.get('privatekey')
    if private_key is None:
        return HttpResponse(
            json.dumps({
                "success": False,
                "message": "No PRIVATEKEY header found.",
            }),
            content_type="application/json",
            status=400
        )
    request_body = request.body
    signature = ethkeys.sign_message(request_body, private_key)
    return HttpResponse(
        json.dumps({
            "success": True,
            "signature": signature,
            "raw_message": request_body.decode('utf-8')
        }),
        content_type="application/json",
        status=200
    )

def forwarder_view(request, *args, **kwargs):
    ''' Forwards requests to desired host. '''
    return HttpResponse(
        json.dumps({
            "success": False,
            "message": "Not implemented (signerserver error)"
        }),
        content_type='application/json',
        status=501
    )
