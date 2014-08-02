import codecs
import logging
import os
import six
from six.moves import queue
import threading

from smiley import db
from smiley import processor

LOG = logging.getLogger(__name__)


class LocalPublisher(processor.EventProcessor):
    """Publish trace data to a database locally.

    We use a separate thread because only the thread that opens the
    database connection can use it, and we want to support
    multi-threaded apps. This will alter the impact smiley has on
    performance of multi-threaded apps, but I expect it to be less
    than having each thread open and close a database handle on
    demand.
    """

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
                q.task_done()
                break
            try:
                self._dispatch_one(the_db, next_data)
            except:
                LOG.exception('error processing %r', next_data)
            q.task_done()
        return

    def _dispatch_one(self, the_db, next_data):
        op, data = next_data
        if op == 'start':
            the_db.start_run(*data)
        elif op == 'end':
            the_db.end_run(*data)
        elif op == 'trace':
            the_db.trace(*data)
        elif op == 'file':
            the_db.cache_file_for_run(*data)
        else:
            LOG.warning('unrecognized data: %r', next_data)

    def _reset_cache(self):
        self._cached_files = set()

    def _stop(self):
        self._q.put(None)
        self._q.join()
        self._db_thread.join()

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
        self._stop()

    def _get_file_contents(self, filename):
        # Should we be decoding the text file here?
        # FIXME: Guess the encoding?
        try:
            with codecs.open(filename, 'r', encoding='utf-8') as f:
                body = f.read()
        except IOError:
            body = six.u('')
        return body

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
            body = self._get_file_contents(filename)
            self._q.put(('file', (run_id, filename, body)))
            # Track the files we have cached so we do not need to
            # re-cache them for the same run.
            self._cached_files.add(filename)
