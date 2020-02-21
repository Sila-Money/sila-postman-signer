import json

from django.http import HttpResponse

JSON_CONTENT_TYPE = "application/json"
DEFAULT_CONTENT_TYPE = JSON_CONTENT_TYPE


def create_json_response(response_body, content_type=DEFAULT_CONTENT_TYPE, status=200, **kwargs):
    """ Returns an instance of django.http.HttpResponse.
        Treats JSON as the default content type and 200 as the default status code.
    """
    if type(response_body) == dict:
        response_body = json.dumps(response_body)
    return HttpResponse(response_body, content_type=content_type, status=status, **kwargs)
