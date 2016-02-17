import argparse
import json
import logging
import traceback
import types
import xml.dom.minidom

from cliff import commandmanager
from six import string_types

LOG = logging.getLogger(__name__)

_CIRCULAR_TYPES = (
    commandmanager.CommandManager,
    logging.Logger,
    types.ModuleType,
    argparse.ArgumentParser,
    xml.dom.minidom.Document,
)


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


def _stringify(data):
    """Convert data to a string if it's not already one"""
    # It's not good enough to just call str(k):
    # In python2 if data is  a `unicode` with non-ascii chars, this will fail.
    return data if isinstance(data, string_types) else str(data)


def _scrub_item(v):
    """Look for a few types that cause circular references.
    """
    if getattr(v, '__module__', None) == 'pkg_resources':
        # Lots of things from pkg_resources seem to have circular
        # references, so just ignore all of them.
        # LOG.debug('replacing pkg_resources type %r', v)
        v = repr(v)
    elif isinstance(v, _CIRCULAR_TYPES):
        # Look for some more specific types from other modules.
        # LOG.debug('replacing %r', v)
        v = repr(v).encode('utf-8')
    elif isinstance(v, dict):
        # Recurse.
        v = _scrub_dict(v)
    elif isinstance(v, list):
        # Recurse.
        v = _scrub_list(v)
    # else:
    #     LOG.debug('keeping object %r of type %s',
    #               v, type(v))
    return v


def _scrub_dict(data):
    return {_stringify(k): _scrub_item(v) for k, v in data.items()}


def _scrub_list(data):
    return [_scrub_item(v) for v in data]


def _scrub(data):
    if isinstance(data, dict):
        data = _scrub_dict(data)
    elif isinstance(data, list):
        data = _scrub_list(data)
    return _scrub_item(data)


def dumps(data):
    data = _scrub(data)
    try:
        return json.dumps(data, default=_json_special_types)
    except ValueError:
        # Circular reference
        # LOG.exception('Could not dump type(%s) %r' % (type(data), data))
        if isinstance(data, list):
            return json.dumps([repr(v) for v in data])
        elif isinstance(data, dict):
            # LOG.debug('trying with repr')
            return json.dumps(
                {_stringify(k): repr(v) for k, v in data.items()})
        raise
