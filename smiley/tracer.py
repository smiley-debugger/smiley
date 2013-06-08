import atexit
import inspect
import logging
import os
import random
import socket
import sys
import time
import uuid

import coverage
from coverage.execfile import run_python_file
from coverage.misc import ExceptionDuringRun

import smiley

LOG = logging.getLogger(__name__)

# Based on similar logic from coverage's control.py, by Ned
# Batchelder, et al.
#
# Look at where some standard modules are located. That's the
# indication for "installed with the interpreter". In some
# environments (virtualenv, for example), these modules may be
# spread across a few locations. Look at all the candidate modules
# we've imported, and take all the different ones.
IGNORE_DIRS = set()
for m in (smiley, coverage, atexit, os, random, socket):
    if hasattr(m, "__file__"):
        IGNORE_DIRS.add(os.path.dirname(m.__file__).rstrip(os.sep) + os.sep)


class TracerContext(object):

    def __init__(self, tracer):
        self.tracer = tracer

    def __enter__(self):
        sys.settrace(self.tracer.trace_calls)
        return self

    def __exit__(self, *args):
        sys.settrace(None)


class Tracer(object):

    def __init__(self, publisher):
        self.publisher = publisher
        self.run_id = None
        self.canonical_filenames = {}

    def _get_interesting_locals(self, frame):
        return {
            n: v
            for n, v in frame.f_locals.items()
            # Ignore any modules, methods, or functions that have made
            # their way into the "locals" namespace for this frame.
            if (not inspect.ismodule(v)
                and not inspect.isfunction(v)
                and not inspect.ismethod(v)
                and (n[:2] != '__' and n[-2:] != '__'))
        }

    def _should_ignore_file(self, filename):
        if not filename:
            return True
        if filename.endswith('>'):
            # builtins?
            return True
        for d in IGNORE_DIRS:
            if filename.startswith(d):
                return True
        return False

    def _send_notice(self, frame, event, arg):
        co = frame.f_code
        func_name = co.co_name
        line_no = frame.f_lineno
        # Expand the filename path to include the full directory so we
        # can decide whether to ignore it or not, and so the remote
        # side knows *exactly* which file we are looking at.
        filename = os.path.abspath(co.co_filename)
        interesting_locals = self._get_interesting_locals(frame)
        self.publisher.send(
            event,
            {'func_name': func_name,
             'line_no': line_no,
             'filename': filename,
             'arg': arg,
             'locals': interesting_locals,
             'timestamp': time.time(),
             'run_id': self.run_id,
             })

    def trace_calls(self, frame, event, arg):
        co = frame.f_code
        filename = co.co_filename
        if filename is not None:
            canonical = self.canonical_filenames.get(filename)
            if canonical is not None:
                filename = canonical
            else:
                full = os.path.abspath(filename)
                self.canonical_filenames[filename] = full
                filename = full
        if self._should_ignore_file(filename):
            return
        self._send_notice(frame, event, arg)
        return self.trace_calls

    def run(self, command_line):
        self.run_id = str(uuid.uuid4())
        try:
            with TracerContext(self):
                self.publisher.send(
                    'start_run',
                    {'run_id': self.run_id,
                     'cwd': os.getcwd(),
                     'command_line': command_line,
                     'timestamp': time.time()},
                )
                run_python_file(
                    command_line[0],
                    command_line,
                )
        except ExceptionDuringRun as err:
            # Unpack the wrapped exception
            err_type, orig_err, traceback = err.args
            try:
                self.publisher.send(
                    'end_run',
                    {'run_id': self.run_id,
                     'message': unicode(orig_err),
                     'traceback': traceback,
                     'timestamp': time.time(),
                     },
                )
            finally:
                del traceback  # remove circular reference for GC
        else:
            self.publisher.send(
                'end_run',
                {'run_id': self.run_id,
                 'timestamp': time.time(),
                 'error': None,
                 'message': None,
                 },
            )
            self.run_id = None
