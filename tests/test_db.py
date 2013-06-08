import fixtures
import testtools

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
        self.assertEqual(row['description'], 'command line would go here')
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
                message=unicode(err),
                traceback=sys.exc_info()[-1],
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
        self.db.trace(
            run_id='12345',
            event='test',
            func_name='test_trace',
            line_no=99,
            filename='test_db.py',
            trace_arg=[{'complex': 'value'}],
            locals={'name': ('value', 'pairs')},
            timestamp=1370436104.65,
        )
        self.db.trace(
            run_id='12345',
            event='test',
            func_name='test_trace',
            line_no=100,
            filename='test_db.py',
            trace_arg=[{'complex': 'value'}],
            locals={'name': ('value', 'pairs')},
            timestamp=1370436104.65,
        )

    def test_insertion_order(self):
        c = self.db.conn.cursor()
        c.execute('select * from trace order by id')
        data = c.fetchall()
        line_nos = [r['line_no'] for r in data]
        self.assertEqual(line_nos, [99, 100])
