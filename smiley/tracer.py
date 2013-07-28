import atexit
import cProfile
import inspect
import logging
import marshal
import os
import pstats
import random
import socket
import sys
import tempfile
import time
import uuid

import coverage
from coverage.execfile import run_python_file
from coverage.misc import ExceptionDuringRun

import smiley
from smiley import uuidstack

LOG = logging.getLogger(__name__)

# Based on similar logic from coverage's control.py, by Ned
# Batchelder, et al.
#
# Look at where some standard modules are located. That's the
# indication for "installed with the interpreter". In some
# environments (virtualenv, for example), these modules may be
# spread across a few locations. Look at all the candidate modules
# we've imported, and take all the different directories.
IGNORE_DIRS = set()
for m in (smiley, coverage, atexit, os, random, socket):
    if hasattr(m, "__file__"):
        IGNORE_DIRS.add(os.path.dirname(m.__file__).rstrip(os.sep) + os.sep)


class TracerContext(object):

    def __init__(self, tracer):
        self.tracer = tracer
        self.profile = cProfile.Profile()

    def __enter__(self):
        self.profile.enable()
        sys.settrace(self.tracer.trace_calls)
        return self

    def __exit__(self, *args):
        sys.settrace(None)
        self.profile.disable()

    def get_stats_data(self):
        stats = pstats.Stats(self.profile)
        with tempfile.TemporaryFile(mode='r+') as f:
            marshal.dump(stats.stats, f)
            f.flush()
            f.seek(0)
            return f.read()


class Tracer(object):

    def __init__(self, publisher):
        self.publisher = publisher
        # FIXME: Use a thread-local
        self.run_id = None
        self.canonical_filenames = {}
        self.uuid_gen = uuidstack.UUIDStack()

    def _get_interesting_locals(self, frame):
        return {
            n: v
            for n, v in frame.f_locals.items()
            # Ignore any modules, methods, or functions that have made
            # their way into the "locals" namespace for this frame.
            if (not inspect.ismodule(v)
                and not inspect.isfunction(v)
                and not inspect.ismethod(v)
                and getattr(getattr(v, '__class__'),
                            '__module__') != '__future__'
                and (n[:2] != '__' and n[-2:] != '__'))
        }

    def _should_ignore_file(self, filename):
        # FIXME: Need to add the ability to explicitly not ignore some
        # things in the stdlib to trace into dependencies.
        if not filename:
            return True
        if filename.endswith('>'):
            # builtins?
            return True
        for d in IGNORE_DIRS:
            if filename.startswith(d):
                return True
        return False

    def _send_notice(self, frame, event, arg, call_id):
        co = frame.f_code
        func_name = co.co_name
        line_no = frame.f_lineno
        # Expand the filename path to include the full directory so we
        # can decide whether to ignore it or not, and so the remote
        # side knows *exactly* which file we are looking at.
        filename = os.path.abspath(co.co_filename)
        interesting_locals = self._get_interesting_locals(frame)
        self.publisher.trace(
            run_id=self.run_id,
            call_id=call_id,
            event=event,
            func_name=func_name,
            line_no=line_no,
            filename=filename,
            trace_arg=arg,
            local_vars=interesting_locals,
            timestamp=time.time(),
        )

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
        if event == 'call':
            call_id = self.uuid_gen.push()
        elif event == 'return':
            call_id = self.uuid_gen.pop()
        else:
            call_id = self.uuid_gen.top()
        self._send_notice(frame, event, arg, call_id)
        return self.trace_calls

    def run(self, command_line):
        self.run_id = str(uuid.uuid4())
        context = TracerContext(self)
        try:
            with context:
                self.publisher.start_run(
                    self.run_id,
                    os.getcwd(),
                    command_line,
                    time.time(),
                )
                run_python_file(
                    command_line[0],
                    command_line,
                )
        except ExceptionDuringRun as err:
            # Unpack the wrapped exception
            err_type, orig_err, traceback = err.args
            try:
                self.publisher.end_run(
                    self.run_id,
                    end_time=time.time(),
                    message=unicode(orig_err),
                    traceback=traceback,
                    stats=context.get_stats_data(),
                )
            finally:
                del traceback  # remove circular reference for GC
        else:
            self.publisher.end_run(
                self.run_id,
                time.time(),
                message=None,
                traceback=None,
                stats=context.get_stats_data(),
            )
            self.run_id = None
