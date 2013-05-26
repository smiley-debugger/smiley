import json

import fixtures
import mock
import testtools
import zmq

from smiley import listener


class ListenerTest(testtools.TestCase):

    def setUp(self):
        super(ListenerTest, self).setUp()
        self.useFixture(fixtures.FakeLogger())

    @mock.patch('zmq.Context')
    def test_socket_setup(self, context_factory):
        listener.Listener('endpoint')
        context = context_factory.return_value
        context.socket.assert_called_with(zmq.PULL)
        s = context.socket.return_value
        s.connect.assert_called_with('endpoint')

    @mock.patch('zmq.Context')
    @mock.patch('smiley.listener.Listener.poll_once')
    def test_poll_breaks(self, meth, context):
        meth.side_effect = KeyboardInterrupt
        cb = mock.MagicMock()
        cb.side_effect = AssertionError('should not be called')
        l = listener.Listener('endpoint')
        l.poll_forever(cb)

    @mock.patch('zmq.Context.socket')
    @mock.patch('zmq.Poller.poll')
    def test_unpack_message(self, poll, socket):
        poll.return_value = [(socket, zmq.POLLIN)]
        msg = {
            'key': 'value',
            'key2': ['v1', 1],
        }
        socket.return_value.recv_multipart.return_value = (
            'message type name',
            json.dumps(msg),
        )
        l = listener.Listener('endpoint')
        val = next(l.poll_once())
        self.assertEqual(val, ['message type name', msg])
