import functools
import logging

from pecan import expose, request
from pecan.rest import RestController

from smiley.presentation import pagination
from smiley.presentation import syntax
from smiley.presentation import trace
from smiley.web import nav
from smiley.web.controllers import files
from smiley.web.controllers import stats

LOG = logging.getLogger(__name__)


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
    def get_one(self, run_id, page=None, per_page=None):
        run = request.db.get_run(run_id)

        session = request.environ['beaker.session']

        # Figure out which page and how many items to show. Look at
        # the session first, because if we don't have valid explicit
        # inputs we will use the session values as defaults. We track
        # the per_page value no matter the run_id for consistency.
        if session.get('run_id') == run_id:
            page = page or session.get('page')
        if page is None:
            page = 1
        per_page = per_page or session.get('per_page') or 20

        if run_id == self._cached_run_id and self._cached_trace:
            LOG.debug('using cached trace for %s', run_id)
            trace_data = self._cached_trace
        else:
            LOG.debug('computing trace for %s', run_id)
            trace_data = list(
                trace.collapse_trace(request.db.get_trace(run_id))
            )
            self._cached_run_id = run_id
            self._cached_trace = trace_data
        syntax_line_cache = syntax.StyledLineCache(request.db, run_id)

        page_vals = pagination.get_pagination_values(
            page, per_page, len(trace_data),
        )
        start = page_vals['start']
        end = page_vals['end']

        def getlines(filename, nums):
            start, end = nums
            return syntax_line_cache.getlines(filename, start, end,
                                              include_comments=True)

        context = {
            'run_id': run_id,
            'run': run,
            'trace': trace_data[start:end],
            'getlines': getlines,
            'getfileid': functools.partial(request.db.get_file_signature,
                                           run_id=run_id),
        }
        context.update(page_vals)

        session['run_id'] = run_id
        session['page'] = page
        session['per_page'] = per_page
        session.save()

        return context
