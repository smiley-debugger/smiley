"""Wrapper around the DB to present a linecache-like interface
for copies of files stored in the db.
"""


class DBLineCache(object):

    def __init__(self, db, run_id):
        self._db = db
        self._run_id = run_id
        self._files = {}

    def _init_file(self, filename):
        if filename not in self._files:
            body = self._db.get_cached_file(self._run_id, filename)
            self._files[filename] = body.splitlines()

    def getline(self, filename, line_no):
        self._init_file(filename)
        try:
            return self._files[filename][line_no-1]
        except IndexError:
            # Line number is out of range
            return ''

    def find_comment_block_start(self, filename, start):
        self._init_file(filename)
        start -= 1  # shift to zero-based index for cache contents
        found_blank = False
        found_comments = False
        search = start - 1
        while search >= 0:
            try:
                line = self._files[filename][search].lstrip()
            except IndexError:
                break
            if not line:
                if found_blank or found_comments:
                    # Stop searching if we find more than one
                    # blank line in a row, or we find a blank line
                    # after having found some comments
                    search += 1
                    break
                else:
                    found_blank = True
                    search -= 1
            elif line[0] == '#':
                found_comments = True
                search -= 1
            else:
                # We didn't find a comment or a blank on this line, so
                # stop looking and use the previously examined line.
                search += 1
                break
        # If we looped around while searching, we can take
        # everything from the start of the file but we don't want
        # a negative index
        if search < 0:
            search = 0
        if found_comments:
            start = search
        return start + 1  # caller is expecting 1-based index

    def getlines(self, filename, start, end, include_comments=False):
        """Return a block of consecutive lines, inclusive.
        """
        if start < 1:
            raise IndexError('start must be >= 1')
        self._init_file(filename)
        if include_comments:
            start = self.find_comment_block_start(filename, start)
        start -= 1  # shift to zero-based index for cache contents
        return '\n'.join(self._files[filename][start:end])
