import functools
import logging

from pecan import expose, request
from pecan.rest import RestController

from smiley import presentation
from smiley.web import nav
from smiley.web.controllers import files
from smiley.web.controllers import stats
from smiley.web import syntax

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
    def get_one(self, run_id, page=1, per_page=20):
        run = request.db.get_run(run_id)

        if run_id == self._cached_run_id and self._cached_trace:
            LOG.debug('using cached trace for %s', run_id)
            trace = self._cached_trace
        else:
            LOG.debug('computing trace for %s', run_id)
            trace = list(
                presentation.collapse_trace(request.db.get_trace(run_id))
            )
            self._cached_run_id = run_id
            self._cached_trace = trace
        syntax_line_cache = syntax.StyledLineCache(request.db, run_id)

        pagination = presentation.get_pagination_values(
            page, per_page, len(trace),
        )
        start = pagination['start']
        end = pagination['end']

        def getlines(filename, nums):
            start, end = nums
            return syntax_line_cache.getlines(filename, start, end,
                                              include_comments=True)

        context = {
            'run_id': run_id,
            'run': run,
            'trace': trace[start:end],
            'getlines': getlines,
            'getfileid': functools.partial(request.db.get_file_signature,
                                           run_id=run_id),
        }
        context.update(pagination)
        return context
