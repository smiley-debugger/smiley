import functools
import logging
import math

from pecan import expose, request
from pecan.rest import RestController

from smiley import db
from smiley import util
from smiley.web import nav
from smiley.web.controllers import files
from smiley.web.controllers import stats
from smiley.web import syntax

LOG = logging.getLogger(__name__)


def collapse_trace(trace_iter):
    """Combine closely related trace items.
    """
    accumulate = None
    for t in trace_iter:
        vars_have_changed = False
        if accumulate:
            vars_that_changed = util.get_variable_changes(
                accumulate.local_vars,
                t.local_vars,
            )
            for var, val in vars_that_changed:
                if var in accumulate.local_vars:
                    # The value of an existing variable changed between events
                    vars_have_changed = True
                    break
        do_yield = (
            accumulate  # we have something to yield
            and
            (vars_have_changed
             or
             accumulate.event != 'line'  # that something can't be collapsed
             or
             t.event != 'line'  # the next event can't be combined with it
             or
             t.event != accumulate.event)
        )
        if do_yield:
            # The events do not match or can't be combined
            yield accumulate
            accumulate = None

        if not accumulate:
            accumulate = db.Trace(
                id=t.id,
                run_id=t.run_id,
                call_id=t.call_id,
                event=t.event,
                filename=t.filename,
                line_no=(t.line_no, t.line_no),
                func_name=t.func_name,
                trace_arg=t.trace_arg,
                local_vars=t.local_vars,
                timestamp=t.timestamp,
            )

        else:
            # Combine consecutive line events by updating the line_no
            # range
            accumulate = db.Trace(
                id=accumulate.id,
                run_id=accumulate.run_id,
                call_id=accumulate.call_id,
                event=accumulate.event,
                filename=accumulate.filename,
                line_no=(accumulate.line_no[0], t.line_no),
                func_name=accumulate.func_name,
                trace_arg=accumulate.trace_arg,
                # replace in case variables were added
                local_vars=t.local_vars,
                timestamp=accumulate.timestamp,
            )

    if accumulate:
        yield accumulate


class RunController(RestController):

    files = files.FileController()
    stats = stats.StatsController()

    _cached_run_id = None
    _cached_trace = None

    @expose(generic=True, template='runs.html')
    @nav.active_section('runs')
    def get_all(self):
        # TODO: Add option to only show error runs
        return {
            'runs': request.db.get_runs(sort_order='DESC'),
        }

    @expose(generic=True, template='run.html')
    @nav.active_section('runs', 'details')
    def get_one(self, run_id, page=1):
        run = request.db.get_run(run_id)

        if run_id == self._cached_run_id and self._cached_trace:
            LOG.debug('using cached trace for %s', run_id)
            trace = self._cached_trace
        else:
            LOG.debug('computing trace for %s', run_id)
            trace = list(collapse_trace(request.db.get_trace(run_id)))
            self._cached_run_id = run_id
            self._cached_trace = trace
        syntax_line_cache = syntax.StyledLineCache(request.db, run_id)

        # PAGINATION MATH
        per_page = 20  # FIXME: module constant? input?
        num_pages = int(math.ceil(len(trace) / (per_page * 1.0)))
        try:
            page = int(page)
        except (TypeError, ValueError):
            page = 1
        if page < 1:
            page = 1
        if page > num_pages:
            page = num_pages

        start = (page - 1) * per_page
        end = start + per_page

        def getlines(filename, nums):
            start, end = nums
            return syntax_line_cache.getlines(filename, start, end,
                                              include_comments=True)

        return {
            'page': page,
            'num_pages': num_pages,
            'run_id': run_id,
            'run': run,
            'trace': trace[start:end],
            'getlines': getlines,
            'getfileid': functools.partial(request.db.get_file_signature,
                                           run_id=run_id),
        }
