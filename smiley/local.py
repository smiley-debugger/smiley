import logging
import os
from six.moves import queue
import threading

from smiley import db
from smiley import processor

LOG = logging.getLogger(__name__)


class LocalPublisher(processor.EventProcessor):

    def __init__(self, database):
        self._reset_cache()
        self._q = queue.Queue()
        self._db_thread = threading.Thread(
            target=self._process_data,
            args=(database, self._q,)
        )
        # We want to kill the thread cleanly, but if something goes
        # wrong trying to start the program we are tracing we don't
        # want smiley to hang, so set the background thread to daemon
        # mode.
        self._db_thread.setDaemon(True)
        self._db_thread.start()

    def _process_data(self, database, q):
        the_db = db.DB(database)
        while True:
            next_data = q.get()
            if next_data is None:
                return
            op, data = next_data
            if op == 'start':
                the_db.start_run(*data)
            elif op == 'end':
                the_db.end_run(*data)
            elif op == 'trace':
                the_db.trace(*data)
            elif op == 'file':
                the_db.cache_file_for_run(*data)

    def _reset_cache(self):
        self._cached_files = set()

    def start_run(self, run_id, cwd, description, start_time):
        """Called when a 'start_run' event is seen.
        """
        self._reset_cache()
        self._cwd = cwd
        if self._cwd:
            self._cwd = self._cwd.rstrip(os.sep) + os.sep
        self._q.put(('start', (run_id, cwd, description, start_time)))

    def end_run(self, run_id, end_time, message, traceback, stats):
        """Called when an 'end_run' event is seen.
        """
        self._q.put(('end', (run_id, end_time, message, traceback, stats)))
        self._q.put(None)

    def trace(self, run_id, thread_id, call_id, event,
              func_name, line_no, filename,
              trace_arg, local_vars,
              timestamp):
        """Called when any other event type is seen.
        """
        self._q.put(
            ('trace',
             (run_id, thread_id, call_id, event, func_name, line_no,
              filename, trace_arg, local_vars, timestamp)))
        if filename and filename not in self._cached_files:
            # Should we be decoding the text file here?
            with open(filename, 'rb') as f:
                body = f.read()
            self._q.put(('file', (run_id, filename, body)))
            # Track the files we have cached so we do not need to
            # re-cache them for the same run.
            self._cached_files.add(filename)
