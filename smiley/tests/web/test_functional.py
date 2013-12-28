# from unittest import TestCase
# from webtest import TestApp
from . import FunctionalTest


class TestRootController(FunctionalTest):

    def test_about(self):
        response = self.app.get('/about')
        self.assertEqual(response.status_int, 200)

    def test_index_redirects(self):
        response = self.app.get('/')
        self.assertEqual(response.status_int, 302)

    def test_get_not_found(self):
        response = self.app.get('/a/bogus/url', expect_errors=True)
        self.assertEqual(response.status_int, 404)
