"""Utility functions for templates
"""


def get_variable_changes(older, newer):
    """Generate sequence of changes between two dictionaries

    Expects to have two variable/namespace dictionaries
    passed as arguments, and it yields the differences
    assuming the first is the older and the second is
    the newer.
    """
    for name in sorted(newer.keys()):
        if name not in older or older[name] != newer[name]:
            yield name, newer[name]
