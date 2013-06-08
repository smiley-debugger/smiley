import json


def _json_special_types(obj):
    # FIXME: Special handling for tracebacks needed.
    return repr(obj)


def dumps(data):
    return json.dumps(data, default=_json_special_types)
