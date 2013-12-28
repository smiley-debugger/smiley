from unittest import TestCase

from smiley import util


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
        self.assertEqual(b['key'], changes['key'])

    def test_change_newkey(self):
        a = {'key': 'value',
             'd': {'dkey': 'dval'}}
        b = {'key': 'value',
             'd': {'dkey': 'dval',
                   'dkey2': 'dval2'}}
        changes = dict(util.get_variable_changes(a, b))
        self.assertIn('d', changes)
        self.assertEqual(b['d'], changes['d'])
