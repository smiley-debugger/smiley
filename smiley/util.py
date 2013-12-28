"""Utility functions for templates
"""

import difflib
from pprint import pformat


def _mk_seq(d):
    return sorted(
        (k, pformat(v, width=20))
        for k, v in d.iteritems()
    )


def get_variable_changes(older, newer):
    """Generate sequence of changes between two dictionaries

    Expects to have two variable/namespace dictionaries
    passed as arguments, and it yields the differences
    assuming the first is the older and the second is
    the newer.
    """
    s_a = _mk_seq(older)
    s_b = _mk_seq(newer)
    matcher = difflib.SequenceMatcher(None, s_a, s_b)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag in {'insert', 'replace'}:
            for i in s_b[j1:j2]:
                yield i
