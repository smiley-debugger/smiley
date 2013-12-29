import testtools

from smiley import db
from smiley.web.controllers import runs


class CollapseTraceTest(testtools.TestCase):

    def test_consecutive_lines(self):
        trace = [
            db.Trace(
                id='1',
                run_id='1',
                call_id='1',
                event='line',
                filename='filename.py',
                line_no=1,
                func_name='func',
                trace_arg={},
                local_vars={},
                timestamp=1,
            ),
            db.Trace(
                id='1',
                run_id='1',
                call_id='1',
                event='line',
                filename='filename.py',
                line_no=2,
                func_name='func',
                trace_arg={},
                local_vars={},
                timestamp=1,
            ),
            db.Trace(
                id='1',
                run_id='1',
                call_id='1',
                event='line',
                filename='filename.py',
                line_no=3,
                func_name='func',
                trace_arg={},
                local_vars={},
                timestamp=1,
            ),
        ]
        collapsed = list(runs.collapse_trace(trace))
        self.assertEqual(len(collapsed), 1)
        line_nos = [r.line_no for r in collapsed]
        self.assertEqual(line_nos, [(1, 3)])

    def test_non_consecutive_lines(self):
        trace = [
            db.Trace(
                id='1',
                run_id='1',
                call_id='1',
                event='line',
                filename='filename.py',
                line_no=1,
                func_name='func',
                trace_arg={},
                local_vars={},
                timestamp=1,
            ),
            db.Trace(
                id='1',
                run_id='1',
                call_id='1',
                event='line',
                filename='filename.py',
                line_no=20,
                func_name='func',
                trace_arg={},
                local_vars={},
                timestamp=1,
            ),
            db.Trace(
                id='1',
                run_id='1',
                call_id='1',
                event='line',
                filename='filename.py',
                line_no=40,
                func_name='func',
                trace_arg={},
                local_vars={},
                timestamp=1,
            ),
        ]
        collapsed = list(runs.collapse_trace(trace))
        self.assertEqual(len(collapsed), 1)
        line_nos = [r.line_no for r in collapsed]
        self.assertEqual(line_nos, [(1, 40)])

    def test_call_lines_return(self):
        trace = [
            db.Trace(
                id='1',
                run_id='1',
                call_id='1',
                event='call',
                filename='filename.py',
                line_no=1,
                func_name='func',
                trace_arg={},
                local_vars={},
                timestamp=1,
            ),
            db.Trace(
                id='1',
                run_id='1',
                call_id='1',
                event='line',
                filename='filename.py',
                line_no=1,
                func_name='func',
                trace_arg={},
                local_vars={},
                timestamp=1,
            ),
            db.Trace(
                id='1',
                run_id='1',
                call_id='1',
                event='line',
                filename='filename.py',
                line_no=2,
                func_name='func',
                trace_arg={},
                local_vars={},
                timestamp=1,
            ),
            db.Trace(
                id='1',
                run_id='1',
                call_id='1',
                event='return',
                filename='filename.py',
                line_no=2,
                func_name='func',
                trace_arg={},
                local_vars={},
                timestamp=1,
            ),
        ]
        collapsed = list(runs.collapse_trace(trace))
        self.assertEqual(len(collapsed), 3)
        line_nos = [r.line_no for r in collapsed]
        self.assertEqual(line_nos, [(1, 1),
                                    (1, 2),
                                    (2, 2)])

    def test_new_var(self):
        trace = [
            db.Trace(
                id='1',
                run_id='1',
                call_id='1',
                event='line',
                filename='filename.py',
                line_no=1,
                func_name='func',
                trace_arg={},
                local_vars={
                    'v1': 1,
                },
                timestamp=1,
            ),
            db.Trace(
                id='1',
                run_id='1',
                call_id='1',
                event='line',
                filename='filename.py',
                line_no=2,
                func_name='func',
                trace_arg={},
                local_vars={
                    'v1': 1,
                    'v2': 2,
                },
                timestamp=1,
            ),
        ]
        collapsed = list(runs.collapse_trace(trace))
        self.assertEqual(len(collapsed), 1)
        self.assertEqual(collapsed[0].local_vars,
                         {'v1': 1, 'v2': 2})

    def test_changed_var(self):
        trace = [
            db.Trace(
                id='1',
                run_id='1',
                call_id='1',
                event='line',
                filename='filename.py',
                line_no=1,
                func_name='func',
                trace_arg={},
                local_vars={
                    'v1': 1,
                    'v3': 3,
                },
                timestamp=1,
            ),
            db.Trace(
                id='1',
                run_id='1',
                call_id='1',
                event='line',
                filename='filename.py',
                line_no=2,
                func_name='func',
                trace_arg={},
                local_vars={
                    'v1': 1,
                    'v2': 2,
                    'v3': 4,
                },
                timestamp=1,
            ),
        ]
        collapsed = list(runs.collapse_trace(trace))
        self.assertEqual(len(collapsed), 2)
        self.assertEqual(collapsed[0].local_vars,
                         {'v1': 1, 'v3': 3})
        self.assertEqual(collapsed[1].local_vars,
                         {'v1': 1, 'v2': 2, 'v3': 4})

    def test_changed_var2(self):
        trace = [
            db.Trace(
                id='1',
                run_id='1',
                call_id='1',
                event='line',
                filename='filename.py',
                line_no=1,
                func_name='func',
                trace_arg={},
                local_vars={
                    'v1': 1,
                    'v3': 3,
                },
                timestamp=1,
            ),
            db.Trace(
                id='1',
                run_id='1',
                call_id='1',
                event='line',
                filename='filename.py',
                line_no=2,
                func_name='func',
                trace_arg={},
                local_vars={
                    'v1': 1,
                    'v2': 2,
                    'v3': 4,
                },
                timestamp=1,
            ),
            # Force the previous data to be emitted, with the next set
            # of local variables being completely different to verify
            # that the variable change detection resets
            db.Trace(
                id='1',
                run_id='1',
                call_id='1',
                event='call',
                filename='filename.py',
                line_no=3,
                func_name='func',
                trace_arg={},
                local_vars={},
                timestamp=1,
            ),
            db.Trace(
                id='1',
                run_id='1',
                call_id='1',
                event='line',
                filename='filename.py',
                line_no=4,
                func_name='func',
                trace_arg={},
                local_vars={
                    'V1': 1,
                },
                timestamp=1,
            ),
            db.Trace(
                id='1',
                run_id='1',
                call_id='1',
                event='line',
                filename='filename.py',
                line_no=5,
                func_name='func',
                trace_arg={},
                local_vars={
                    'V1': 1,
                    'V2': 2,
                },
                timestamp=1,
            ),
        ]
        collapsed = list(runs.collapse_trace(trace))
        self.assertEqual(len(collapsed), 4)
        self.assertEqual(collapsed[0].local_vars,
                         {'v1': 1, 'v3': 3})
        self.assertEqual(collapsed[1].local_vars,
                         {'v1': 1, 'v2': 2, 'v3': 4})
        self.assertEqual(collapsed[3].local_vars,
                         {'V1': 1, 'V2': 2})
