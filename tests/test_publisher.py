import fixtures
import mock
import testtools
import zmq

from smiley import publisher


class PublisherTest(testtools.TestCase):

    def setUp(self):
        super(PublisherTest, self).setUp()
        self.useFixture(fixtures.FakeLogger())

    def test_socket_setup(self):
        with mock.patch('zmq.Context') as context_factory:
            publisher.Publisher('endpoint', 999)
            context = context_factory.return_value
            context.socket.assert_called_with(zmq.PUSH)
            s = context.socket.return_value
            s.bind.assert_called_with('endpoint')
            self.assertEqual(s.hwm, 999)
