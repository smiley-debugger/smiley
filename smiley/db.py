import collections
import contextlib
import datetime
import hashlib
import json
import logging
import pkgutil
import sqlite3

from smiley import jsonutil
from smiley import processor

LOG = logging.getLogger(__name__)


Run = collections.namedtuple(
    'Run',
    'id cwd description start_time end_time error_message',
)


def _make_run(row):
    return Run(
        row['id'],
        row['cwd'],
        json.loads(row['description']),
        (datetime.datetime.fromtimestamp(row['start_time'])
         if row['start_time'] else None),
        (datetime.datetime.fromtimestamp(row['end_time'])
         if row['end_time'] else None),
        row['error_message'],
    )


Trace = collections.namedtuple(
    'Trace',
    ' '.join(['id', 'run_id', 'call_id', 'event',
              'filename', 'line_no', 'func_name',
              'trace_arg', 'local_vars',
              'timestamp'])
)


def _make_trace(row):
    return Trace(
        row['id'],
        row['run_id'],
        row['call_id'],
        row['event'],
        row['filename'],
        row['line_no'],
        row['func_name'],
        json.loads(row['trace_arg']),
        json.loads(row['local_vars']),
        row['timestamp'],
    )


@contextlib.contextmanager
def transaction(conn):
    c = conn.cursor()
    try:
        yield c
    except:
        conn.rollback()
        raise
    else:
        conn.commit()


class DB(processor.EventProcessor):
    """Database connection and API.
    """

    def __init__(self, name):
        self.conn = sqlite3.connect(name)
        # Use Row, instead of just lists/tuples
        self.conn.row_factory = sqlite3.Row
        # Try to select some data and create the schema if we can't.
        try:
            cursor = self.conn.cursor()
            cursor.execute('select * from run')
            LOG.debug('database already initialized')
        except sqlite3.OperationalError:
            LOG.debug('initializing database')
            schema = pkgutil.get_data('smiley', 'schema.sql')
            cursor.executescript(schema)
        return

    def start_run(self, run_id, cwd, description, start_time):
        "Record the beginning of a run."
        with transaction(self.conn) as c:
            c.execute(
                """
                INSERT INTO run (id, cwd, description, start_time)
                VALUES (:id, :cwd, :description, :start_time)
                """,
                {'id': run_id,
                 'cwd': cwd,
                 'description': jsonutil.dumps(description),
                 'start_time': start_time}
            )

    def end_run(self, run_id, end_time, message, traceback):
        "Record the end of a run."
        with transaction(self.conn) as c:
            c.execute(
                """
                UPDATE run
                SET
                    end_time = :end_time,
                    error_message = :message,
                    traceback = :traceback
                WHERE id = :id
                """,
                {'id': run_id,
                 'end_time': end_time,
                 'message': message,
                 'traceback': jsonutil.dumps(traceback)},
            )

    def get_runs(self, only_errors=False, sort_order='ASC'):
        "Return the run data."
        query = ["SELECT * FROM run"]
        if only_errors:
            query.append("WHERE error_message is not null")
        query.append("ORDER BY start_time %s" % sort_order)
        with transaction(self.conn) as c:
            c.execute(' '.join(query))
            return (_make_run(r) for r in c.fetchall())

    def get_run(self, run_id):
        "Return the run data."
        with transaction(self.conn) as c:
            c.execute(
                "SELECT * FROM run WHERE id = :run_id",
                {'run_id': run_id},
            )
            return _make_run(c.fetchone())

    def trace(self, run_id, call_id, event,
              func_name, line_no, filename,
              trace_arg, local_vars,
              timestamp):
        "Record an event during a run."
        with transaction(self.conn) as c:
            c.execute(
                """
                INSERT INTO trace
                (run_id, call_id, event,
                 func_name, line_no, filename,
                 trace_arg, local_vars,
                 timestamp)
                VALUES
                (:run_id, :call_id, :event,
                 :func_name, :line_no, :filename,
                 :trace_arg, :local_vars,
                 :timestamp)
                """,
                {'run_id': run_id,
                 'call_id': call_id,
                 'event': event,
                 'func_name': func_name,
                 'line_no': line_no,
                 'filename': filename,
                 'trace_arg': jsonutil.dumps(trace_arg),
                 'local_vars': jsonutil.dumps(local_vars),
                 'timestamp': timestamp,
                 }
            )

    def get_trace(self, run_id):
        "Return the run data."
        with transaction(self.conn) as c:
            c.execute(
                "SELECT * FROM trace WHERE run_id = :run_id ORDER BY id",
                {'run_id': run_id},
            )
            return (_make_trace(t)
                    for t in c.fetchall())

    def cache_file_for_run(self, run_id, filename, body):
        signature_maker = hashlib.sha1()
        signature_maker.update(filename)
        signature_maker.update(body)
        signature = signature_maker.hexdigest()
        with transaction(self.conn) as c:
            try:
                c.execute(
                    """
                    INSERT INTO file (signature, name, body)
                    VALUES (:signature, :filename, :body)
                    """,
                    {'signature': signature,
                     'filename': filename,
                     'body': body,
                     },
                )
            except sqlite3.IntegrityError:
                pass
            try:
                c.execute(
                    """
                    INSERT INTO run_file
                    (run_id, signature)
                    VALUES (:run_id, :signature)
                    """,
                    {'run_id': run_id,
                     'signature': signature,
                     },
                )
            except sqlite3.IntegrityError:
                pass

    def get_cached_file(self, run_id, filename):
        with transaction(self.conn) as c:
            c.execute(
                """
                SELECT body
                FROM file JOIN run_file USING (signature)
                WHERE
                  name = :filename
                  AND
                  run_id = :run_id
                """,
                {'filename': filename,
                 'run_id': run_id,
                 },
            )
            row = c.fetchone()
            return row['body'] if row else ''
