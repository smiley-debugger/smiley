import logging
import os

from smiley import db
from smiley import processor

LOG = logging.getLogger(__name__)


class LocalPublisher(processor.EventProcessor):

    def __init__(self, database):
        self.db = db.DB(database)
        self._reset_cache()

    def _reset_cache(self):
        self._cached_files = set()

    def start_run(self, run_id, cwd, description, start_time):
        """Called when a 'start_run' event is seen.
        """
        self._reset_cache()
        self._cwd = cwd
        if self._cwd:
            self._cwd = self._cwd.rstrip(os.sep) + os.sep
        self.db.start_run(run_id, cwd, description, start_time)

    def end_run(self, run_id, end_time, message, traceback, stats):
        """Called when an 'end_run' event is seen.
        """
        self.db.end_run(run_id, end_time, message, traceback, stats)

    def trace(self, run_id, call_id, event,
              func_name, line_no, filename,
              trace_arg, local_vars,
              timestamp):
        """Called when any other event type is seen.
        """
        self.db.trace(run_id, call_id, event, func_name, line_no,
                      filename, trace_arg, local_vars, timestamp)
        if filename and filename not in self._cached_files:
            # Should we be decoding the text file here?
            with open(filename, 'rb') as f:
                body = f.read()
            self.db.cache_file_for_run(
                run_id,
                filename,
                body,
            )
            # Track the files we have cached so we do not need to
            # re-cache them for the same run.
            self._cached_files.add(filename)
