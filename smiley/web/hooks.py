from pecan import hooks

from smiley import db


class DBHook(hooks.PecanHook):
    """Set up database for request.

    Attach a database object to the request so we don't have to create
    a new one each time.

    """

    def __init__(self, database_name):
        super(DBHook, self).__init__()
        self._db = db.DB(database_name)

    def before(self, state):
        state.request.db = self._db
