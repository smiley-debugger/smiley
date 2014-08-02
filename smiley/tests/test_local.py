import unittest

import mock
from smiley import local


class LocalTest(unittest.TestCase):

    def setUp(self):
        super(LocalTest, self).setUp()
        self.pub = local.LocalPublisher(':memory:')
        # Shutdown the thread started inside the publisher
        self.pub._stop()

    def test_start_run(self):
        # Mock out the queue because end_run() expects to be able to
        # call _stop() but we've already done that and calling it
        # again may hang.
        with mock.patch.object(self.pub, '_q') as q:
            self.pub.start_run(
                '12345',
                '/no/such/dir',
                'command line would go here',
                1370436103.65,
            )
            expected = ('start',
                        ('12345', mock.ANY,
                         'command line would go here',
                         1370436103.65),
                        )
            q.put.assert_called_once_with(expected)

    def test_end_run(self):
        # Mock out the queue because end_run() expects to be able to
        # call _stop() but we've already done that and calling it
        # again may hang.
        with mock.patch.object(self.pub, '_q') as q:
            self.pub.end_run(
                run_id='12345',
                end_time=1370436103.65,
                message='error message here',
                traceback=None,
                stats=None,
            )
            expected = [
                mock.call(('end',
                           ('12345', 1370436103.65, 'error message here',
                            None, None))),
                mock.call(None),
            ]
            self.assertEqual(expected, q.put.call_args_list)
            q.join.assert_called_with()

    def test_trace(self):
        # Mock out the queue because end_run() expects to be able to
        # call _stop() but we've already done that and calling it
        # again may hang.
        with mock.patch.object(self.pub, '_q') as q:
            with mock.patch.object(self.pub, '_get_file_contents') as gfc:
                gfc.return_value = 'body here'
                self.pub.trace(
                    run_id='12345',
                    thread_id='t1',
                    call_id='c1',
                    event='foo',
                    func_name='func',
                    line_no=1,
                    filename='file.py',
                    trace_arg={},
                    local_vars={},
                    timestamp=1370436103.65,
                )
                expected = [
                    mock.call(('trace',
                               ('12345', 't1', 'c1', 'foo', 'func', 1,
                                'file.py', {}, {},
                                1370436103.65))),
                    mock.call(('file',
                               ('12345', 'file.py', 'body here'))),
                ]
                self.assertEqual(expected, q.put.call_args_list)

    def test_trace_file_in_cache(self):
        # Mock out the queue because end_run() expects to be able to
        # call _stop() but we've already done that and calling it
        # again may hang.
        with mock.patch.object(self.pub, '_q') as q:
            with mock.patch.object(self.pub, '_get_file_contents') as gfc:
                gfc.return_value = 'body here'
                self.pub._cached_files.add('file.py')
                self.pub.trace(
                    run_id='12345',
                    thread_id='t1',
                    call_id='c1',
                    event='foo',
                    func_name='func',
                    line_no=1,
                    filename='file.py',
                    trace_arg={},
                    local_vars={},
                    timestamp=1370436103.65,
                )
                expected = [
                    mock.call(('trace',
                               ('12345', 't1', 'c1', 'foo', 'func', 1,
                                'file.py', {}, {},
                                1370436103.65))),
                ]
                self.assertEqual(expected, q.put.call_args_list)

    def test_process_start(self):
        the_db = mock.Mock()
        self.pub._dispatch_one(the_db, ('start', ('args',)))
        the_db.start_run.assert_called_once_with('args')

    def test_process_end(self):
        the_db = mock.Mock()
        self.pub._dispatch_one(the_db, ('end', ('args',)))
        the_db.end_run.assert_called_once_with('args')

    def test_process_trace(self):
        the_db = mock.Mock()
        self.pub._dispatch_one(the_db, ('trace', ('args',)))
        the_db.trace.assert_called_once_with('args')

    def test_process_file(self):
        the_db = mock.Mock()
        self.pub._dispatch_one(the_db, ('file', ('args',)))
        the_db.cache_file_for_run.assert_called_once_with('args')
