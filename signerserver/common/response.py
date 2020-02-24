import json
import wsgiref

from django.http import HttpResponse

JSON_CONTENT_TYPE = "application/json"
DEFAULT_CONTENT_TYPE = JSON_CONTENT_TYPE


def create_json_response(response_body, content_type=DEFAULT_CONTENT_TYPE, status=200, headers=None, **kwargs):
    """ Returns an instance of django.http.HttpResponse.
        Treats JSON as the default content type and 200 as the default status code.
    """
    if type(response_body) == dict:
        response_body = json.dumps(response_body)
    response = HttpResponse(response_body, content_type=content_type, status=status, **kwargs)
    if type(headers) == dict:
        for header in headers:
            if not wsgiref.util.is_hop_by_hop(header):
                response[header] = headers[header]
    return response
