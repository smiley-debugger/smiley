from pecan import expose, request
from webob.exc import status_map

from smiley.web import nav
from smiley import db_linecache


class RootController(object):

    @expose(generic=True, template='index.html')
    @nav.active_section('runs')
    def index(self):
        # TODO: Add option to only show error runs
        return {
            'runs': request.db.get_runs(sort_order='DESC'),
        }

    @expose('error.html')
    def error(self, status):
        try:
            status = int(status)
        except ValueError:  # pragma: no cover
            status = 500
        message = getattr(status_map.get(status), 'explanation', '')
        return dict(status=status, message=message)

    @expose(generic=True, template='about.html')
    @nav.active_section('about')
    def about(self):
        return {}

    @expose(generic=True, template='run.html')
    @nav.active_section('runs')
    def runs(self, run_id):
        run = request.db.get_run(run_id)
        trace = request.db.get_trace(run_id)
        line_cache = db_linecache.DBLineCache(request.db, run_id)
        return {
            'run_id': run_id,
            'run': run,
            'trace': trace,
            'getline': line_cache.getline,
        }
