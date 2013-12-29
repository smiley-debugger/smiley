import base64
import collections
import contextlib
import datetime
import hashlib
import json
import logging
import pkgutil
import pstats
import sqlite3
import tempfile

import six

from smiley import jsonutil
from smiley import processor

LOG = logging.getLogger(__name__)


Run = collections.namedtuple(
    'Run',
    'id cwd description start_time end_time error_message stats',
)


def _make_run(row):
    # HACK: It really is too bad that pstats can't load data from
    # a string.
    if row['stats']:
        with tempfile.NamedTemporaryFile(mode='w') as f:
            f.write(base64.b64decode(row['stats']))
            f.flush()
            stats = pstats.Stats(f.name)
    else:
        stats = None
    return Run(
        row['id'],
        row['cwd'],
        json.loads(row['description']),
        (datetime.datetime.fromtimestamp(row['start_time'])
         if row['start_time'] else None),
        (datetime.datetime.fromtimestamp(row['end_time'])
         if row['end_time'] else None),
        row['error_message'],
        stats,
    )


File = collections.namedtuple(
    'File',
    'name signature run_id',
)


def _make_file(row):
    return File(
        row['name'],
        row['signature'],
        row['run_id'],
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
        id=row['id'],
        run_id=row['run_id'],
        call_id=row['call_id'],
        event=row['event'],
        filename=row['filename'],
        line_no=row['line_no'],
        func_name=row['func_name'],
        trace_arg=json.loads(row['trace_arg']),
        local_vars=json.loads(row['local_vars']),
        timestamp=datetime.datetime.fromtimestamp(row['timestamp']),
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
            cursor.execute(u'select * from run')
            LOG.debug('database already initialized')
        except sqlite3.OperationalError:
            LOG.debug('initializing database')
            schema = pkgutil.get_data('smiley', 'schema.sql').decode('utf-8')
            cursor.executescript(schema)
        return

    def start_run(self, run_id, cwd, description, start_time):
        "Record the beginning of a run."
        with transaction(self.conn) as c:
            c.execute(
                u"""
                INSERT INTO run (id, cwd, description, start_time)
                VALUES (:id, :cwd, :description, :start_time)
                """,
                {'id': run_id,
                 'cwd': cwd,
                 'description': jsonutil.dumps(description),
                 'start_time': start_time}
            )

    def end_run(self, run_id, end_time, message, traceback, stats):
        "Record the end of a run."
        with transaction(self.conn) as c:
            c.execute(
                u"""
                UPDATE run
                SET
                    end_time = :end_time,
                    error_message = :message,
                    traceback = :traceback,
                    stats = :stats
                WHERE id = :id
                """,
                {'id': run_id,
                 'end_time': end_time,
                 'message': message,
                 'traceback': jsonutil.dumps(traceback),
                 'stats': base64.b64encode(stats) if stats else None},
            )

    def get_runs(self, only_errors=False, sort_order='ASC'):
        "Return the run data."
        query = [u"SELECT * FROM run"]
        if only_errors:
            query.append(u"WHERE error_message is not null")
        query.append(u"ORDER BY start_time %s" % sort_order)
        with transaction(self.conn) as c:
            c.execute(u' '.join(query))
            return (_make_run(r) for r in c.fetchall())

    def get_run(self, run_id):
        "Return the run data."
        with transaction(self.conn) as c:
            c.execute(
                u"SELECT * FROM run WHERE id = :run_id",
                {'run_id': run_id},
            )
            return _make_run(c.fetchone())

    def trace(self, run_id, call_id, event,
              func_name, line_no, filename,
              trace_arg, local_vars,
              timestamp):
        "Record an event during a run."
        #LOG.debug('trace(filename=%s)', filename)
        with transaction(self.conn) as c:
            c.execute(
                u"""
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
                u"SELECT * FROM trace WHERE run_id = :run_id ORDER BY id",
                {'run_id': run_id},
            )
            return (_make_trace(t)
                    for t in c.fetchall())

    def cache_file_for_run(self, run_id, filename, body):
        signature_maker = hashlib.sha1()
        if isinstance(filename, six.text_type):
            signature_maker.update(filename.encode('utf-8'))
        else:
            signature_maker.update(filename)
        if isinstance(body, six.text_type):
            signature_maker.update(body.encode('utf-8'))
        else:
            signature_maker.update(body)
        signature = signature_maker.hexdigest()
        with transaction(self.conn) as c:
            try:
                c.execute(
                    u"""
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
                    u"""
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
        return signature

    def get_file_signature(self, run_id, filename):
        """Return the file signature for the named file within the run.
        """
        #LOG.debug('get_file_signature(%s)', filename)
        with transaction(self.conn) as c:
            c.execute(
                u"""
                SELECT signature
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
            #LOG.debug(' -> %s', row)
            return row['signature'] if row else ''

    def get_files_for_run(self, run_id):
        with transaction(self.conn) as c:
            c.execute(
                u"""
                SELECT name, signature, run_id
                FROM file JOIN run_file USING (signature)
                WHERE
                  run_id = :run_id
                ORDER BY name ASC
                """,
                {'run_id': run_id,
                 },
            )
            return (_make_file(row) for row in c.fetchall())

    def get_cached_file(self, run_id, filename):
        with transaction(self.conn) as c:
            c.execute(
                u"""
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

    def get_cached_file_by_id(self, run_id, file_id):
        with transaction(self.conn) as c:
            c.execute(
                u"""
                SELECT name, body
                FROM file JOIN run_file USING (signature)
                WHERE
                  signature = :signature
                  AND
                  run_id = :run_id
                """,
                {'signature': file_id,
                 'run_id': run_id,
                 },
            )
            row = c.fetchone()
            return (row['name'], row['body']) if row else ('', '')
