import json
import traceback
import types


def _json_special_types(obj):
    if isinstance(obj, types.TracebackType):
        return traceback.extract_tb(obj)
    if isinstance(obj, type):
        # We don't want to return classes
        return repr(obj)
    try:
        data = dict(vars(obj))
        data['__class__'] = obj.__class__.__name__
        data['__module__'] = obj.__class__.__module__
        if isinstance(obj, Exception) and 'args' not in data:
            try:
                data['args'] = obj.args
            except AttributeError:
                pass
    except Exception:
        data = repr(obj)
    return data


def dumps(data):
    return json.dumps(data, default=_json_special_types)
