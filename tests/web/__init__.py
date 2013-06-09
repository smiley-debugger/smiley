from unittest import TestCase
from pecan import set_config
from pecan.testing import load_test_app

from smiley.web import config

__all__ = ['FunctionalTest']


class FunctionalTest(TestCase):
    """
    Used for functional tests where you need to test your
    literal application and its integration with the framework.
    """

    def setUp(self):
        self.app = load_test_app(
            config.get_config_dict(':memory:'),
        )

    def tearDown(self):
        set_config({}, overwrite=True)
