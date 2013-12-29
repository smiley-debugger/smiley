import fixtures
import json
import testtools

import six

from smiley import db


class TransactionTest(testtools.TestCase):

    def setUp(self):
        super(TransactionTest, self).setUp()
        self.useFixture(fixtures.FakeLogger())
        self.db = db.DB(':memory:')

    def test_commit(self):
        with db.transaction(self.db.conn) as c:
            c.execute(
                """
                INSERT INTO run (id, cwd, description, start_time)
                VALUES ('12345', 'cwd-here', 'useful description',
                        1370436103.65)
                """)

            db2 = db.DB(':memory:')
            c2 = db2.conn.cursor()
            c2.execute('select * from run')
            d = c2.fetchall()
            self.assertEqual(d, [])

        c3 = self.db.conn.cursor()
        c3.execute('select * from run')
        d = c3.fetchall()
        self.assertEqual(len(d), 1)

    def test_rollback(self):
        try:
            with db.transaction(self.db.conn) as c:
                c.execute(
                    """
                    INSERT INTO run (id, cwd, description, start_time)
                    VALUES ('12345', 'cwd-here', 'useful description',
                            1370436103.65)
                    """)

                db2 = db.DB(':memory:')
                c2 = db2.conn.cursor()
                c2.execute('select * from run')
                d = c2.fetchall()
                self.assertEqual(d, [])
                raise RuntimeError('testing')
        except RuntimeError as err:
            self.assertEqual(str(err), 'testing')

        c3 = self.db.conn.cursor()
        c3.execute('select * from run')
        d = c3.fetchall()
        self.assertEqual(len(d), 0)


class DBTest(testtools.TestCase):

    def setUp(self):
        super(DBTest, self).setUp()
        self.useFixture(fixtures.FakeLogger())
        self.db = db.DB(':memory:')

    def test_start_run(self):
        self.db.start_run(
            '12345',
            '/no/such/dir',
            'command line would go here',
            1370436103.65,
        )
        c = self.db.conn.cursor()
        c.execute('select * from run')
        data = c.fetchall()
        self.assertEqual(len(data), 1)
        row = data[0]
        self.assertEqual(row['id'], '12345')
        self.assertEqual(row['cwd'], '/no/such/dir')
        self.assertEqual(row['description'], '"command line would go here"')
        self.assertEqual(row['start_time'], 1370436103.65)
        self.assertEqual(row['end_time'], None)
        self.assertEqual(row['error_message'], None)
        self.assertEqual(row['traceback'], None)

    def test_end_run_clean(self):
        self.db.start_run(
            '12345',
            '/no/such/dir',
            'command line would go here',
            1370436103.65,
        )
        self.db.end_run(
            '12345',
            1370436104.65,
            message=None,
            traceback=None,
            stats=None,
        )
        c = self.db.conn.cursor()
        c.execute('select * from run')
        data = c.fetchall()
        self.assertEqual(len(data), 1)
        row = data[0]
        self.assertEqual(row['id'], '12345')
        self.assertEqual(row['start_time'], 1370436103.65)
        self.assertEqual(row['end_time'], 1370436104.65)

    def test_end_run_traceback(self):
        self.db.start_run(
            '12345',
            '/no/such/dir',
            'command line would go here',
            1370436103.65,
        )
        try:
            raise RuntimeError('test exception')
        except RuntimeError as err:
            import sys
            self.db.end_run(
                '12345',
                1370436104.65,
                message=six.text_type(err),
                traceback=sys.exc_info()[-1],
                stats=None,
            )
        c = self.db.conn.cursor()
        c.execute('select * from run')
        data = c.fetchall()
        self.assertEqual(len(data), 1)
        row = data[0]
        self.assertEqual(row['id'], '12345')
        self.assertEqual(row['error_message'], 'test exception')
        # FIXME: Need to serialize the traceback better
        assert 'traceback' in row['traceback']


class TraceTest(testtools.TestCase):

    def setUp(self):
        super(TraceTest, self).setUp()
        self.useFixture(fixtures.FakeLogger())
        self.db = db.DB(':memory:')
        self.db.start_run(
            '12345',
            '/no/such/dir',
            'command line would go here',
            1370436103.65,
        )
        self.local_values = {'name': ['value', 'pairs']}
        self.trace_arg = [{'complex': 'value'}]
        self.db.trace(
            run_id='12345',
            call_id='abcd',
            event='test',
            func_name='test_trace',
            line_no=99,
            filename='test_db.py',
            trace_arg=self.trace_arg,
            local_vars=self.local_values,
            timestamp=1370436104.65,
        )
        self.db.trace(
            run_id='12345',
            call_id='abcd',
            event='test',
            func_name='test_trace',
            line_no=100,
            filename='test_db.py',
            trace_arg=self.trace_arg,
            local_vars=self.local_values,
            timestamp=1370436104.65,
        )

    def test_insertion_order(self):
        c = self.db.conn.cursor()
        c.execute('select * from trace order by id')
        data = c.fetchall()
        line_nos = [r['line_no'] for r in data]
        self.assertEqual(line_nos, [99, 100])

    def test_local_vars(self):
        c = self.db.conn.cursor()
        c.execute('select * from trace order by id')
        row = c.fetchone()
        self.assertEqual(json.loads(row['local_vars']),
                         self.local_values)

    def test_trace_arg(self):
        c = self.db.conn.cursor()
        c.execute('select * from trace order by id')
        row = c.fetchone()
        self.assertEqual(json.loads(row['trace_arg']),
                         self.trace_arg)


class QueryTest(testtools.TestCase):

    def setUp(self):
        super(QueryTest, self).setUp()
        self.useFixture(fixtures.FakeLogger())
        self.db = db.DB(':memory:')
        self.db.start_run(
            '12345',
            '/no/such/dir',
            ['command', 'line', 'would', 'go', 'here'],
            1370436103.65,
        )
        self.local_values = {'name': ['value', 'pairs']}
        self.trace_arg = [{'complex': 'value'}]
        self.db.trace(
            run_id='12345',
            call_id='abcd',
            event='test',
            func_name='test_trace',
            line_no=99,
            filename='test_db.py',
            trace_arg=self.trace_arg,
            local_vars=self.local_values,
            timestamp=1370436104.65,
        )
        self.db.trace(
            run_id='12345',
            call_id='abcd',
            event='test',
            func_name='test_trace',
            line_no=100,
            filename='test_db.py',
            trace_arg=self.trace_arg,
            local_vars=self.local_values,
            timestamp=1370436104.65,
        )
        self.db.start_run(
            '6789',
            '/no/such/dir',
            ['command', 'line', 'would', 'go', 'here'],
            1370436104.65,
        )
        self.db.end_run(
            '6789',
            1370436105.65,
            'error message',
            None,
            stats=None,
        )

    def test_get_runs(self):
        runs = list(self.db.get_runs())
        self.assertEqual(len(runs), 2)
        self.assertEqual(runs[0].id, '12345')
        self.assertEqual(runs[1].id, '6789')

    def test_get_runs_desc(self):
        runs = list(self.db.get_runs(sort_order='DESC'))
        self.assertEqual(len(runs), 2)
        self.assertEqual(runs[0].id, '6789')
        self.assertEqual(runs[1].id, '12345')

    def test_get_runs_errors(self):
        runs = list(self.db.get_runs(True))
        self.assertEqual(len(runs), 1)
        self.assertEqual(runs[0].id, '6789')

    def test_get_run(self):
        run = self.db.get_run('12345')
        self.assertEqual(run.id, '12345')
        self.assertEqual(
            run.description,
            ['command', 'line', 'would', 'go', 'here']
        )

    def test_get_trace(self):
        trace = list(self.db.get_trace('12345'))
        self.assertEqual(len(trace), 2)
        line_nos = [r.line_no for r in trace]
        self.assertEqual(line_nos, [99, 100])


class FileCacheTest(testtools.TestCase):

    def setUp(self):
        super(FileCacheTest, self).setUp()
        self.useFixture(fixtures.FakeLogger())
        self.db = db.DB(':memory:')
        self.db.start_run(
            '12345',
            '/no/such/dir',
            ['command', 'line', 'would', 'go', 'here'],
            1370436103.65,
        )
        self.db.start_run(
            '6789',
            '/no/such/dir',
            ['command', 'line', 'would', 'go', 'here'],
            1370436103.65,
        )

    def test_add_file(self):
        self.db.cache_file_for_run(
            '12345',
            'test-file.txt',
            'this would be the body',
        )
        c = self.db.conn.cursor()
        c.execute('select * from file')
        rows = list(c.fetchall())
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row['body'], 'this would be the body')
        self.assertEqual(row['name'], 'test-file.txt')

    def test_add_file_twice_same(self):
        self.db.cache_file_for_run(
            '12345',
            'test-file.txt',
            'this would be the body',
        )
        self.db.cache_file_for_run(
            '12345',
            'test-file.txt',
            'this would be the body',
        )
        c = self.db.conn.cursor()
        c.execute('select * from file')
        rows = list(c.fetchall())
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row['body'], 'this would be the body')
        self.assertEqual(row['name'], 'test-file.txt')

    def test_add_file_twice_different(self):
        self.db.cache_file_for_run(
            '12345',
            'test-file.txt',
            'this would be the body',
        )
        self.db.cache_file_for_run(
            '12345',
            'test-file.txt',
            'this body has changed',
        )
        c = self.db.conn.cursor()
        c.execute('select * from file')
        rows = list(c.fetchall())
        self.assertEqual(len(rows), 2)

    def test_retrieve_via_name(self):
        self.db.cache_file_for_run(
            '12345',
            'test-file.txt',
            'this would be the body',
        )
        body = self.db.get_cached_file(
            '12345',
            'test-file.txt',
        )
        self.assertEqual(body, 'this would be the body')

    def test_retrieve_via_signature(self):
        signature = self.db.cache_file_for_run(
            '12345',
            'test-file.txt',
            'this would be the body',
        )
        name, body = self.db.get_cached_file_by_id(
            '12345',
            signature,
        )
        self.assertEqual(name, 'test-file.txt')
        self.assertEqual(body, 'this would be the body')

    def test_retrieve_signature(self):
        signature = self.db.cache_file_for_run(
            '12345',
            'test-file.txt',
            'this would be the body',
        )
        actual = self.db.get_file_signature(
            '12345',
            'test-file.txt',
        )
        self.assertEqual(signature, actual)

    def test_retrieve_from_run_bad_id(self):
        self.db.cache_file_for_run(
            '12345',
            'test-file.txt',
            'this would be the body',
        )
        body = self.db.get_cached_file(
            '6789',  # wrong run id
            'test-file.txt',
        )
        self.assertEqual(body, '')

    def test_retrieve_from_run_bad_name(self):
        self.db.cache_file_for_run(
            '12345',
            'test-file.txt',
            'this would be the body',
        )
        body = self.db.get_cached_file(
            '12345',
            'no-such-file.txt',
        )
        self.assertEqual(body, '')

    def test_list_files(self):
        self.db.cache_file_for_run(
            '12345',
            'test-file.txt',
            'this would be the body',
        )
        self.db.cache_file_for_run(
            '12345',
            'test-file2.txt',
            'this would be the body',
        )
        files = list(self.db.get_files_for_run('12345'))
        self.assertEqual(2, len(files))
        names = [f.name for f in files]
        self.assertEqual(['test-file.txt', 'test-file2.txt'], names)
