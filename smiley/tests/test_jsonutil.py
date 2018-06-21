import traceback

import fixtures
import testtools

import six

from smiley import jsonutil


class JSONTest(testtools.TestCase):

    def setUp(self):
        super(JSONTest, self).setUp()
        self.useFixture(fixtures.FakeLogger())

    def test_traceback(self):
        try:
            raise RuntimeError('here')
        except RuntimeError:
            import sys
            expected = traceback.extract_tb(sys.exc_info()[-1])
            actual = jsonutil._json_special_types(sys.exc_info()[-1])
        self.assertEqual(expected, actual)

    def test_exception(self):
        err = RuntimeError('here')
        actual = jsonutil._json_special_types(err)
        if six.PY3:
            expected = {
                '__class__': 'RuntimeError',
                '__module__': 'builtins',
                'args': ('here',),
            }
        else:
            expected = {
                '__class__': 'RuntimeError',
                '__module__': 'exceptions',
                'args': ('here',),
            }
        self.assertEqual(expected, actual)

    def test_exception_with_complex_object(self):
        err = RuntimeError(self)
        actual = jsonutil._json_special_types(err)
        if six.PY3:
            expected = {
                '__class__': 'RuntimeError',
                '__module__': 'builtins',
                'args': (self,),
            }
        else:
            expected = {
                '__class__': 'RuntimeError',
                '__module__': 'exceptions',
                'args': (self,),
            }
        self.assertEqual(expected, actual)

    def test_arbitrary_object(self):
        class Foo(object):
            def __init__(self):
                self.a = 'A'
                self.b = 'B'
        expected = {
            '__class__': 'Foo',
            '__module__': 'smiley.tests.test_jsonutil',
            'a': 'A',
            'b': 'B',
        }
        actual = jsonutil._json_special_types(Foo())
        self.assertEqual(expected, actual)

    def test_arbitrary_object_old_style(self):
        class Foo:
            def __init__(self):
                self.a = 'A'
                self.b = 'B'
        expected = {
            '__class__': 'Foo',
            '__module__': 'smiley.tests.test_jsonutil',
            'a': 'A',
            'b': 'B',
        }
        actual = jsonutil._json_special_types(Foo())
        self.assertEqual(expected, actual)

    def test_type(self):
        if six.PY2:
            expected = "<type 'int'>"
        else:
            expected = "<class 'int'>"
        actual = jsonutil._json_special_types(int)
        self.assertEqual(expected, actual)

    def test_dict_tuple_keys(self):
        """Keys in dicts should be converted to strings"""
        actual = jsonutil.dumps({(1, 2): 3})
        expected = '{"(1, 2)": 3}'
        self.assertEqual(expected, actual)
