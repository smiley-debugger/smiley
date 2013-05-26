import json
import logging

import zmq

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
        msg = [
            msg_type,
            json.dumps(data, default=self._json_special_types),
        ]
        LOG.debug('SENDING: %r', msg)
        self.pub_socket.send_multipart(msg)
