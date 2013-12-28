import json

import fixtures
import mock
import testtools
import zmq

from smiley import publisher


class PublisherTest(testtools.TestCase):

    def setUp(self):
        super(PublisherTest, self).setUp()
        self.useFixture(fixtures.FakeLogger())

    @mock.patch('zmq.Context')
    def test_socket_setup(self, context_factory):
        publisher.Publisher('endpoint', 999)
        context = context_factory.return_value
        context.socket.assert_called_with(zmq.PUSH)
        s = context.socket.return_value
        s.bind.assert_called_with('endpoint')
        self.assertEqual(s.hwm, 999)

    @mock.patch('zmq.Context.socket')
    def test_message_format(self, socket):
        p = publisher.Publisher('endpoint', 999)
        msg = {
            'key': 'value',
            'key2': ['v1', 1],
        }
        p._send('message type name', msg)
        s = socket.return_value
        s.send_multipart.assert_called_with(
            ['message type name', json.dumps(msg)]
        )
