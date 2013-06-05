import json
import logging

import zmq
import sys

LOG = logging.getLogger(__name__)


class Publisher(object):

    def __init__(self, endpoint, high_water_mark=10000):
        self.context = zmq.Context()
        self.pub_socket = self.context.socket(zmq.PUSH)
        self.pub_socket.bind(endpoint)
        self.pub_socket.identity = 'publisher'
        self.pub_socket.hwm = high_water_mark

    def _json_special_types(self, obj):
        return repr(obj)

    def send(self, msg_type, data):
        old_trace = None
        try:
            old_trace = sys.gettrace()
            sys.settrace(None)
            msg = [
                msg_type,
                json.dumps(data, default=self._json_special_types),
            ]
            LOG.debug('SENDING: %r', msg)
            self.pub_socket.send_multipart(msg)
        finally:
            if old_trace is not None:
                sys.settrace(old_trace)
