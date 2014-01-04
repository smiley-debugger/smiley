"""Wrapper around the DB to present a linecache-like interface
for copies of files stored in the db, with pygments styles applied.
"""
import logging

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import guess_lexer_for_filename

from smiley import db_linecache

LOG = logging.getLogger(__name__)


def apply_style(filename, body, linenos=True, theme='default'):
    """Apply the syntax highlighter to the given file.
    """
    lexer = guess_lexer_for_filename(filename, body)
    formatter = HtmlFormatter(linenos=linenos)
    return highlight(body, lexer, formatter)


def syntax(body):
    """Filter for applying syntax highlighting to blocks from templates."""
    return apply_style('unknown.py', body, linenos=False)


class StyledLineCache(object):

    def __init__(self, db, run_id):
        self._db = db
        self._run_id = run_id
        self._files = {}
        self._plain_line_cache = db_linecache.DBLineCache(db, run_id)

    EXPECTED_PREFIX = '<div class="highlight"><pre>'
    EXPECTED_SUFFIX = '</pre></div>'

    def _init_file(self, filename):
        if filename not in self._files:
            body = self._db.get_cached_file(self._run_id, filename)
            styled_body = apply_style(filename, body, linenos=False)
            start = len(self.EXPECTED_PREFIX)
            end = -1 * (len(self.EXPECTED_SUFFIX) + 1)
            middle_body = styled_body[start:end].rstrip('\n')
            self._files[filename] = middle_body.splitlines()

    def getline(self, filename, line_no):
        #LOG.debug('getline(%s, %s)', filename, line_no)
        self._init_file(filename)
        try:
            return self._files[filename][line_no-1]
        except IndexError:
            # Line number is out of range
            return ''

    def getlines(self, filename, start, end, include_comments=False):
        """Return a block of consecutive lines.
        """
        if start < 1:
            raise IndexError('start must be >= 1')
        self._init_file(filename)
        if include_comments:
            start = self._plain_line_cache.find_comment_block_start(
                filename,
                start,
            )
        return '\n'.join(self._files[filename][start-1:end])
