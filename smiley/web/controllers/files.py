from pecan import expose, request
from pecan.rest import RestController

from smiley.web import nav
from smiley.web import syntax


class FileController(RestController):

    @expose(generic=True, template='file.html')
    @nav.active_section('runs', 'files')
    def get_one(self, run_id, file_id):
        filename, body = request.db.get_cached_file_by_id(run_id, file_id)
        run = request.db.get_run(run_id)

        styled_body = syntax.apply_style(filename, body)

        return {
            'run_id': run_id,
            'run': run,
            'filename': filename,
            'body': body,
            'styled_body': styled_body,
        }

    @expose(generic=True, template='files.html')
    @nav.active_section('runs', 'files')
    def get_all(self, run_id):
        # TODO: Add option to only show error runs
        run = request.db.get_run(run_id)
        return {
            'run': run,
            'files': request.db.get_files_for_run(run_id),
            'run_id': run_id,
        }
