import functools

from pecan import expose, request
from pecan.rest import RestController

from smiley.web import nav
from smiley.web.controllers import files
from smiley.web.controllers import stats
from smiley.web import syntax


class RunController(RestController):

    files = files.FileController()
    stats = stats.StatsController()

    @expose(generic=True, template='runs.html')
    @nav.active_section('runs')
    def get_all(self):
        # TODO: Add option to only show error runs
        return {
            'runs': request.db.get_runs(sort_order='DESC'),
        }

    @expose(generic=True, template='run.html')
    @nav.active_section('runs', 'details')
    def get_one(self, run_id):
        run = request.db.get_run(run_id)
        trace = request.db.get_trace(run_id)
        line_cache = syntax.StyledLineCache(request.db, run_id)
        return {
            'run_id': run_id,
            'run': run,
            'trace': trace,
            'getline': line_cache.getline,
            'getfileid': functools.partial(request.db.get_file_signature,
                                           run_id=run_id),
        }
