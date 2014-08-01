from pecan import expose, request
from pecan.rest import RestController

from smiley.presentation import syntax
from smiley.web import nav
from smiley.web.controllers import run_context


class FileController(RestController):

    @expose(generic=True, template='file.html')
    @nav.active_section('runs', 'files')
    def get_one(self, run_id, file_id):
        filename, body = request.db.get_cached_file_by_id(run_id, file_id)
        styled_body = syntax.apply_style(filename, body)

        context = run_context.get_context(request.db, run_id, None)
        context.update({
            'filename': filename,
            'body': body,
            'styled_body': styled_body,
        })
        return context

    @expose(generic=True, template='files.html')
    @nav.active_section('runs', 'files')
    def get_all(self, run_id):
        # TODO: Add option to only show error runs
        context = run_context.get_context(request.db, run_id, None)
        context.update({
            'files': request.db.get_files_for_run(run_id),
        })
        return context
