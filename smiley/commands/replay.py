import logging

from cliff import command

from smiley import db
from smiley import db_linecache
from smiley import output


class Replay(command.Command):
    """Query the database and replay a previously captured run.

    """

    log = logging.getLogger(__name__)

    _cwd = None

    def get_parser(self, prog_name):
        parser = super(Replay, self).get_parser(prog_name)
        parser.add_argument(
            '--database',
            default='smiley.db',
            help='filename for the database (%(default)s)',
        )
        parser.add_argument(
            'run_id',
            help='identifier for the run',
        )
        return parser

    def take_action(self, parsed_args):
        self.db = db.DB(parsed_args.database)
        cache = db_linecache.DBLineCache(self.db, parsed_args.run_id)
        self.out = output.OutputFormatter(cache.getline)

        run_details = self.db.get_run(parsed_args.run_id)
        self.out.start_run(
            run_details.id,
            run_details.cwd,
            run_details.description,
            run_details.start_time,
        )
        for t in self.db.get_trace(parsed_args.run_id):
            self.out.trace(
                t.run_id,
                t.event,
                t.func_name,
                t.line_no,
                t.filename,
                t.trace_arg,
                t.local_vars,
                t.timestamp,
            )
        self.out.end_run(
            run_details.id,
            run_details.end_time,
            run_details.error_message,
            None,  # run_details.traceback,
        )
