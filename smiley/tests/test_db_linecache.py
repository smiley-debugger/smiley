import fixtures
import testtools

from smiley import db
from smiley import db_linecache


class DBFileCacheTest(testtools.TestCase):

    def setUp(self):
        super(DBFileCacheTest, self).setUp()
        self.useFixture(fixtures.FakeLogger())
        self.db = db.DB(':memory:')
        self.db.start_run(
            '12345',
            '/no/such/dir',
            ['command', 'line', 'would', 'go', 'here'],
            1370436103.65,
        )
        self.db.cache_file_for_run(
            '12345',
            'test-file.txt',
            'this would be the body\nline two\nline three',
        )
        self.cache = db_linecache.DBLineCache(self.db, '12345')

    def test_file_and_line_exist(self):
        line = self.cache.getline('test-file.txt', 2)
        self.assertEqual(line, 'line two')

    def test_file_does_not_exist(self):
        line = self.cache.getline('no-such-test-file.txt', 2)
        self.assertEqual(line, '')

    def test_line_does_not_exist(self):
        line = self.cache.getline('test-file.txt', 99)
        self.assertEqual(line, '')
