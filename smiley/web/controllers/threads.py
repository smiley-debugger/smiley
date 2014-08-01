from pecan import expose, request
from pecan.rest import RestController

from smiley.web import nav
from smiley.web.controllers import run_context


class ThreadController(RestController):

    @expose(generic=True, template='threads.html')
    @nav.active_section('runs', 'threads')
    def get_all(self, run_id):
        return run_context.get_context(request.db, run_id, None)
