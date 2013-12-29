"""Manage a "stack" of UUID values for unique entries into a function.

The owner of the stack manages when calls enter and exit.

"""

import uuid

import six


class UUIDStack(object):

    def __init__(self):
        self._stack = []

    def top(self):
        if not self._stack:
            return None
        return self._stack[-1]

    def push(self):
        self._stack.append(six.text_type(uuid.uuid4()))

    def pop(self):
        return self._stack.pop()
