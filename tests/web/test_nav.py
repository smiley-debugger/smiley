from unittest import TestCase

from pecan import expose

from smiley.web import nav


class NavDecoratorTest(TestCase):

    def test_active_section_before_expose(self):
        @nav.active_section('test')
        @expose(generic=True, template='index.html')
        def func():
            return {}
        result = func()
        self.assertTrue('active_section' in result)
        self.assertEqual(result['active_section'], 'test')

    def test_active_section_after_expose(self):
        @expose(generic=True, template='index.html')
        @nav.active_section('test')
        def func():
            return {}
        result = func()
        self.assertTrue('active_section' in result)
        self.assertEqual(result['active_section'], 'test')

    def test_active_section_rendered_template(self):
        @nav.active_section('test')
        def func():
            return ''
        result = func()
        self.assertFalse('active_section' in result)
