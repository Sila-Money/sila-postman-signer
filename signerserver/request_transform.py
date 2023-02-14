"""Contains helper functions for transforming a request to be forwarded."""

import hashlib
import json
import uuid
from datetime import datetime
from typing import Optional, Tuple


def modify_json_request_body(
        request_body: str,
        set_epoch_field: Optional[str] = None,
        set_uuid_field: Optional[str] = None,
        set_file_hash_field: Optional[Tuple[str, object]] = None,
        set_file_metadata_field: Optional[Tuple[str, object]] = None,
) -> str:
    """Modifies request body if set_epoch_field or set_uuid_field is not None."""
    if set_epoch_field or set_uuid_field:
        json_dict = json.loads(request_body)
        if set_epoch_field:
            set_current_epoch_in_dict(json_dict, str(set_epoch_field).lower().split("."))

        if set_uuid_field:
            set_value_in_dict(json_dict, str(set_uuid_field).lower().split("."), str(uuid.uuid4()))

        if set_file_hash_field:
            hash_location = str(set_file_hash_field[0]).lower().split(".")
            file_hash = generate_sha256_file_hash(set_file_hash_field[1])
            set_value_in_dict(json_dict, hash_location, file_hash)

        if set_file_metadata_field:
            file_name_key, mime_type_key = [x.strip() for x in str(set_file_metadata_field[0]).lower().split(',')]
            file_storage = set_file_metadata_field[1]
            set_value_in_dict(json_dict, [file_name_key], file_storage.filename)

        request_body = json.dumps(json_dict)
    return request_body


def scrub_request_headers(initial_headers: dict, scrub_list=None) -> dict:
    """
    Removes certain headers from the request before forwarding to new host.
    If scrub_list is None, removes no headers.
    Returns dictionary of headers that didn't match the scrub_list.
    """
    if scrub_list is None:
        scrub_list = []
    caps_sensitive_scrub_list = []

    for header in initial_headers:
        if len(scrub_list) == len(caps_sensitive_scrub_list):
            break

        for header_to_scrub in scrub_list:
            if header.lower() == header_to_scrub.lower():
                caps_sensitive_scrub_list.append(header)
                break

    # this is done because you can't change the
    # length of an iterable while iterating over it
    for pop_header in caps_sensitive_scrub_list:
        initial_headers.pop(pop_header)

    return initial_headers


def generate_sha256_file_hash(f):
    hasher = hashlib.sha256()
    hasher.update(f.read())
    file_hash = hasher.hexdigest()
    f.seek(0)
    return file_hash


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
