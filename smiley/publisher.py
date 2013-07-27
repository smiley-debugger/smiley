import logging

import zmq
import sys

from smiley import jsonutil
from smiley import processor

LOG = logging.getLogger(__name__)


class Publisher(processor.EventProcessor):

    def __init__(self, endpoint, high_water_mark=10000):
        self.context = zmq.Context()
        self.pub_socket = self.context.socket(zmq.PUSH)
        self.pub_socket.bind(endpoint)
        self.pub_socket.identity = 'publisher'
        self.pub_socket.hwm = high_water_mark

    def _send(self, msg_type, data):
        old_trace = None
        try:
            old_trace = sys.gettrace()
            sys.settrace(None)
            msg = [
                msg_type,
                jsonutil.dumps(data),
            ]
            LOG.debug('SENDING: %r', msg)
            self.pub_socket.send_multipart(msg)
        finally:
            if old_trace is not None:
                sys.settrace(old_trace)

    def start_run(self, run_id, cwd, description, start_time):
        """Called when a 'start_run' event is seen.
        """
        self._send(
            'start_run',
            {'run_id': run_id,
             'cwd': cwd,
             'command_line': description,
             'timestamp': start_time,
             },
        )

    def end_run(self, run_id, end_time, message, traceback, stats):
        """Called when an 'end_run' event is seen.
        """
        self._send(
            'end_run',
            {'run_id': run_id,
             'timestamp': end_time,
             'message': message,
             'traceback': traceback,
             'stats': stats,
             },
        )

    def trace(self, run_id, call_id, event,
              func_name, line_no, filename,
              trace_arg, local_vars,
              timestamp):
        """Called when any other event type is seen.
        """
        self._send(
            event,
            {'func_name': func_name,
             'line_no': line_no,
             'filename': filename,
             'arg': trace_arg,
             'local_vars': local_vars,
             'timestamp': timestamp,
             'run_id': run_id,
             'call_id': call_id,
             })
