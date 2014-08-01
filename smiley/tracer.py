import atexit
import cProfile
import imp
import inspect
import logging
import os
import pstats
import random
import site
import socket
import sys
import threading
import time
import uuid

import coverage
from coverage.execfile import run_python_file
from coverage.misc import ExceptionDuringRun

import smiley
from smiley.stats import stats_to_blob
from smiley import uuidstack

LOG = logging.getLogger(__name__)


class TracerContext(object):

    def __init__(self, tracer):
        self.tracer = tracer
        self.profile = cProfile.Profile()

    def __enter__(self):
        self.profile.enable()
        sys.settrace(self.tracer.trace_calls)
        threading.settrace(self.tracer.trace_calls)
        return self

    def __exit__(self, *args):
        sys.settrace(None)
        threading.settrace(None)
        self.profile.disable()

    def get_stats_data(self):
        stats = pstats.Stats(self.profile)
        return stats_to_blob(stats)


class Tracer(object):

    def _canonical_path(self, path):
        return os.path.abspath(path.rstrip(os.sep)) + os.sep

    def _canonical_parent(self, filename):
        return self._canonical_path(
            os.path.dirname(os.path.realpath(filename))
        )

    def __init__(self, publisher,
                 include_stdlib=False,
                 include_site_packages=True,
                 include_packages=[]):
        self.publisher = publisher
        # FIXME: Use a thread-local
        self.run_id = None
        self.canonical_filenames = {}
        self.uuid_gen = uuidstack.UUIDStack()

        # Build the list of paths to ignore or include, based on
        # similar logic from coverage's control.py, by Ned Batchelder,
        # et al.

        # Always default to ignoring smiley and the coverage module.
        self._ignore_dirs = set()
        for m in [smiley, coverage]:
            if hasattr(m, "__file__"):
                to_ignore = self._canonical_parent(m.__file__)
                LOG.debug('ignoring packages under %s based on %s',
                          to_ignore, m.__name__)
                self._ignore_dirs.add(to_ignore)

        # If we are not supposed to include the stdlib, we need to
        # look at where some standard modules are located. That's the
        # indication for "installed with the interpreter". In some
        # environments (virtualenv, for example), these modules may be
        # spread across a few locations. Look at all the candidate
        # modules we've imported, and take all the different
        # directories.
        self._stdlibdirs = set()
        if not include_stdlib:
            d = self._canonical_path(os.path.join(
                sys.prefix,
                'lib',
                'python%s.%s' % sys.version_info[:2],
            ))
            self._stdlibdirs.add(d)
            LOG.debug('ignoring stdlib %s', d)
            for m in [atexit, os, random, socket, site]:
                if hasattr(m, "__file__"):
                    to_ignore = self._canonical_parent(m.__file__)
                    LOG.debug('ignoring packages under %s based on %s',
                              to_ignore, m.__name__)
                    self._stdlibdirs.add(to_ignore)
            LOG.debug('ignoring stdlib packages from %s',
                      sorted(self._stdlibdirs))
        else:
            LOG.debug('including stdlib')

        # If the user wants us to include some specific packages, find
        # them so we can include those directories even if they are
        # under the stdlib or site-packages, which we might be
        # ignoring separately.
        self._include_packages = set()
        for name in include_packages:
            try:
                f, filename, description = imp.find_module(name)
                if f:
                    f.close()
            except ImportError as e:
                LOG.info('Could not find %r to include it: %s',
                         name, e)
            else:
                to_include = self._canonical_parent(filename)
                LOG.debug('including packages under %s', to_include)
                self._include_packages.add(to_include)
        LOG.debug('including packages from %s', sorted(self._include_packages))

        # Since the site-packages directory is under the standard
        # library location, we have to handle that directory here so
        # it can be checked separately from the standard library
        # location.
        if include_site_packages:
            # Use a package we know we require (so it is likely to be
            # installed) but is not smiley (which will not work in a
            # test environment) to find the site-packages directory.
            import cliff
            site_packages = self._canonical_parent(
                self._canonical_parent(cliff.__file__)
            )
            LOG.debug('including site-packages %s', site_packages)
            self._sitepkgdir = site_packages
        else:
            self._sitepkgdir = None

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
        # LOG.debug('_should_ignore_file(%s)', filename)
        if not filename:
            return True
        if filename.endswith('>'):
            # builtins?
            # LOG.debug('ignoring builtin %s', filename)
            return True
        filename = os.path.realpath(filename)
        for d in self._include_packages:
            # LOG.debug('checking include package %s', d)
            if filename.startswith(d):
                # LOG.debug('including package %s', filename)
                return False
        for d in self._ignore_dirs:
            # LOG.debug('checking ignore directory %s', d)
            if filename.startswith(d):
                # LOG.debug('ignoring package %s', filename)
                return True
        if self._sitepkgdir:
            # LOG.debug('checking site-packages %s', self._sitepkgdir)
            if filename.startswith(self._sitepkgdir):
                # LOG.debug('including %s', filename)
                return False
        for d in self._stdlibdirs:
            # LOG.debug('checking stdlib %s', d)
            if filename.startswith(d):
                # LOG.debug('ignoring stdlib %s', filename)
                return True
        # LOG.debug('defaulting to including %s', filename)
        return False

    def _send_notice(self, thread_id, frame, event, arg, call_id):
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
            thread_id=thread_id,
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
        thread_id = threading.currentThread().name
        self._send_notice(thread_id, frame, event, arg, call_id)
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
