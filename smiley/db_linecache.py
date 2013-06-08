"""Wrapper around the DB to present a linecache-like interface
for copies of files stored in the db.
"""


class DBLineCache(object):

    def __init__(self, db, run_id):
        self._db = db
        self._run_id = run_id
        self._files = {}

    def getline(self, filename, line_no):
        if filename not in self._files:
            body = self._db.get_cached_file(self._run_id, filename)
            self._files[filename] = body.splitlines()
        try:
            return self._files[filename][line_no]
        except IndexError:
            # Line number is out of range
            return ''
