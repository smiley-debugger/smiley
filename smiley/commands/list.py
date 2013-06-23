import logging

from cliff import lister

from smiley import db


def _format_timestamp(t):
    if t is None:
        return ''
    return t.isoformat()


class List(lister.Lister):
    """Query the database and show the existing runs.

    """

    log = logging.getLogger(__name__)

    _cwd = None

    DEFAULT_COLUMNS = (
        'id', 'cwd', 'description',
        'start time', 'end time',
        'error message',
    )

    def get_parser(self, prog_name):
        parser = super(List, self).get_parser(prog_name)
        parser.add_argument(
            '--database',
            default='smiley.db',
            help='filename for the database (%(default)s)',
        )
        parser.add_argument(
            '--errors',
            default=False,
            action='store_true',
            help='only include runs with errors',
        )
        return parser

    def take_action(self, parsed_args):
        self.db = db.DB(parsed_args.database)
        runs = ((r.id, r.cwd,
                 ' '.join(r.description),
                 _format_timestamp(r.start_time),
                 _format_timestamp(r.end_time),
                 r.error_message)
                for r in self.db.get_runs(only_errors=parsed_args.errors))
        return (self.DEFAULT_COLUMNS, runs)
