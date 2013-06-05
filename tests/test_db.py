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
