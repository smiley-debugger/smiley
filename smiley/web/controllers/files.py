from pecan import expose, request
from pecan.rest import RestController

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import guess_lexer_for_filename

from smiley.web import nav


class FileController(RestController):

    @expose(generic=True, template='file.html')
    @nav.active_section('runs')
    def get_one(self, run_id, file_id):
        filename, body = request.db.get_cached_file_by_id(run_id, file_id)
        run = request.db.get_run(run_id)

        lexer = guess_lexer_for_filename(filename, body)
        formatter = HtmlFormatter(linenos=True)
        styled_body = highlight(body, lexer, formatter)

        return {
            'run_id': run_id,
            'run': run,
            'filename': filename,
            'body': body,
            'styled_body': styled_body,
        }
