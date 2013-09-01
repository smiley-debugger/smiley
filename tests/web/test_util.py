import pprint
from unittest import TestCase

from smiley.web import util


class TestGetVariableChanges(TestCase):

    def test_addition(self):
        a = {}
        b = {'new': 'value'}
        changes = dict(util.get_variable_changes(a, b))
        self.assertIn('new', changes)

    def test_deletion(self):
        a = {'new': 'value'}
        b = {}
        changes = dict(util.get_variable_changes(a, b))
        self.assertNotIn('new', changes)

    def test_change(self):
        a = {'key': 'value'}
        b = {'key': 'newvalue'}
        changes = dict(util.get_variable_changes(a, b))
        self.assertIn('key', changes)
        self.assertEqual(pprint.pformat(b['key']), changes['key'])
