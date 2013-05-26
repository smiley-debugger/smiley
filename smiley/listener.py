import json
import logging

import zmq

LOG = logging.getLogger(__name__)


class Listener(object):

    def __init__(self, endpoint):
        self.context = zmq.Context()
        self.sub_socket = self.context.socket(zmq.PULL)
        self.sub_socket.connect(endpoint)
        self.sub_socket.identity = 'subscriber'
        self.poller = zmq.Poller()
        self.poller.register(self.sub_socket, zmq.POLLIN)

    def poll_once(self, timeout=1000):
        for sock, reason in self.poller.poll(timeout):
            if reason != zmq.POLLIN:
                return
            # Receiving data on the subscriber socket
            msg_type, msg_data = self.sub_socket.recv_multipart()
            yield [
                msg_type,
                json.loads(msg_data),
            ]

    def poll_forever(self, callback, timeout=1000):
        LOG.debug('Waiting for incoming data')
        while True:
            try:
                for m in self.poll_once(timeout):
                    callback(m)
            except KeyboardInterrupt:
                break
