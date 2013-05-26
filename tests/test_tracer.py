import atexit

import fixtures
import mock
import testtools

from smiley import tracer


class TracerTest(testtools.TestCase):

    def setUp(self):
        super(TracerTest, self).setUp()
        self.useFixture(fixtures.FakeLogger())

    def test_interesting_locals(self):
        def _func():
            pass
        t = tracer.Tracer(None)
        f = mock.Mock()
        f.f_locals = {
            'simple_name': 1,
            'module': tracer,
            'function': _func,
            'method': self.setUp,
            '__magic__': 2,
        }
        interesting = t._get_interesting_locals(f)
        self.assertEqual(interesting, {'simple_name': 1})

    def test_ignore_stdlib(self):
        t = tracer.Tracer(None)
        self.assertTrue(t._should_ignore_file(atexit.__file__))

    def test_ignore_smiley(self):
        t = tracer.Tracer(None)
        self.assertTrue(t._should_ignore_file(tracer.__file__))

    # @mock.patch('zmq.Context')
    # def test_socket_setup(self, context_factory):
    #     listener.Listener('endpoint')
    #     context = context_factory.return_value
    #     context.socket.assert_called_with(zmq.PULL)
    #     s = context.socket.return_value
    #     s.connect.assert_called_with('endpoint')

    # @mock.patch('zmq.Context')
    # @mock.patch('smiley.listener.Listener.poll_once')
    # def test_poll_breaks(self, meth, context):
    #     meth.side_effect = KeyboardInterrupt
    #     cb = mock.MagicMock()
    #     cb.side_effect = AssertionError('should not be called')
    #     l = listener.Listener('endpoint')
    #     l.poll_forever(cb)

    # @mock.patch('zmq.Context.socket')
    # @mock.patch('zmq.Poller.poll')
    # def test_unpack_message(self, poll, socket):
    #     poll.return_value = [(socket, zmq.POLLIN)]
    #     msg = {
    #         'key': 'value',
    #         'key2': ['v1', 1],
    #     }
    #     socket.return_value.recv_multipart.return_value = (
    #         'message type name',
    #         json.dumps(msg),
    #     )
    #     l = listener.Listener('endpoint')
    #     val = next(l.poll_once())
    #     self.assertEqual(val, ['message type name', msg])
