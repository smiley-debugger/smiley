import zmq


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
                print 'reason:', reason
                return
            # Receiving data on the subscriber socket
            yield self.sub_socket.recv_multipart()

    def poll_forever(self, callback, timeout=1000):
        print 'Waiting for incoming data'
        while True:
            try:
                for m in self.poll_once(timeout):
                    callback(m)
            except KeyboardInterrupt:
                break
