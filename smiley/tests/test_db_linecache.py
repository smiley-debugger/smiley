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
        self.db.cache_file_for_run(
            '12345',
            'with-comments.txt',
            '\n'.join([
                '# start comment',
                'line two',
                '',
                '  # middle comment',
                '',
                'end line',
                '# comment',
                'last line',
            ]),
        )
        self.db.cache_file_for_run(
            '12345',
            'multi-line-comments.txt',
            '\n'.join([
                '# start comment',
                '# comment line 2',
                'non-comment 1',
                '',
                '  # middle comment',
                '  # middle comment line 2',
                '',
                'middle line',
                '# last comment',
                '# last comment line 2',
                'last line',
            ]),
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

    def test_range_exists(self):
        lines = self.cache.getlines('test-file.txt', 2, 3)
        self.assertEqual(lines, 'line two\nline three')

    def test_range_underflow(self):
        self.assertRaises(IndexError,
                          self.cache.getlines,
                          'test-file.txt', 0, 2,
                          )

    def test_range_overflow(self):
        lines = self.cache.getlines('test-file.txt', 2, 4)
        self.assertEqual(lines, 'line two\nline three')

    def test_find_comments_adjascent(self):
        start = self.cache.find_comment_block_start('with-comments.txt', 2)
        self.assertEqual(start, 1)

    def test_comments_adjascent(self):
        lines = self.cache.getlines('with-comments.txt', 2, 2,
                                    include_comments=True)
        self.assertEqual(lines, '# start comment\nline two')

    def test_multi_line_comments_adjascent(self):
        lines = self.cache.getlines('multi-line-comments.txt', 3, 3,
                                    include_comments=True)
        self.assertEqual(
            lines,
            '# start comment\n# comment line 2\nnon-comment 1',
        )

    def test_find_comments_none(self):
        start = self.cache.find_comment_block_start('test-file.txt', 2)
        self.assertEqual(start, 2)

    def test_comments_none(self):
        lines = self.cache.getlines('test-file.txt', 2, 3,
                                    include_comments=True)
        self.assertEqual(lines, 'line two\nline three')

    def test_find_comments_and_blank_line(self):
        start = self.cache.find_comment_block_start('with-comments.txt', 6)
        self.assertEqual(start, 4)

    def test_comments_and_blank_line(self):
        lines = self.cache.getlines('with-comments.txt', 6, 6,
                                    include_comments=True)
        self.assertEqual(lines, '  # middle comment\n\nend line')

    def test_multi_line_comments_and_blank_line(self):
        lines = self.cache.getlines('multi-line-comments.txt', 8, 8,
                                    include_comments=True)
        self.assertEqual(
            lines,
            '  # middle comment\n  # middle comment line 2\n\nmiddle line',
        )

    def test_find_comments_without_blank_line(self):
        start = self.cache.find_comment_block_start('with-comments.txt', 8)
        self.assertEqual(start, 7)

    def test_comments_without_blank_line(self):
        lines = self.cache.getlines('with-comments.txt', 8, 8,
                                    include_comments=True)
        self.assertEqual(lines, '# comment\nlast line')

    def test_multi_line_comments_without_blank_line(self):
        lines = self.cache.getlines('multi-line-comments.txt', 11, 11,
                                    include_comments=True)
        self.assertEqual(
            lines,
            '# last comment\n# last comment line 2\nlast line',
        )
