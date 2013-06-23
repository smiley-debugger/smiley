from pecan import expose, redirect
from webob.exc import status_map

from smiley.web import nav
from smiley.web.controllers.runs import RunController


class RootController(object):

    runs = RunController()

    @expose(generic=True)
    def index(self):
        redirect('/runs')

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
