import atexit
import os

import mock
import testtools

from smiley import tracer


class TracerTest(testtools.TestCase):

    # def setUp(self):
    #     super(TracerTest, self).setUp()

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

    def test_ignore_stdlib_maybe_c(self):
        # The atexit module is implemented in C in python 3.3, so it
        # has a different filename and path than under 2.7
        t = tracer.Tracer(None, include_stdlib=False)
        self.assertTrue(t._should_ignore_file(atexit.__file__))

    def test_ignore_stdlib(self):
        t = tracer.Tracer(None, include_stdlib=False)
        self.assertTrue(t._should_ignore_file(os.__file__))

    def test_capture_stdlib(self):
        t = tracer.Tracer(None, include_stdlib=True)
        self.assertFalse(t._should_ignore_file(atexit.__file__))

    def test_ignore_smiley(self):
        t = tracer.Tracer(None)
        self.assertTrue(t._should_ignore_file(tracer.__file__))

    def test_include_smiley(self):
        t = tracer.Tracer(None, include_packages=['smiley'])
        self.assertFalse(t._should_ignore_file(tracer.__file__))

    def test_ignore_site_packages(self):
        t = tracer.Tracer(None, include_site_packages=False)
        self.assertTrue(t._should_ignore_file(mock.__file__))

    def test_include_site_packages(self):
        t = tracer.Tracer(None, include_site_packages=True)
        self.assertFalse(t._should_ignore_file(mock.__file__))
