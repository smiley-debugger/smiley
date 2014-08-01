import logging

from cliff import command

from smiley import db
from smiley import output


class Show(command.Command):
    """Show the details of one run.

    Includes summaries of the thread resource consumption, when
    multiple threads are present.
    """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Show, self).get_parser(prog_name)
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
        run = self.db.get_run(parsed_args.run_id)
        details = {
            'id': run.id,
            'cwd': run.cwd,
            'description': run.description,
            'start_time': run.start_time.isoformat(),
            'end_time': run.end_time.isoformat(),
            'error_message': run.error_message,
            'traceback': run.traceback,
        }
        output.dump_dictionary(details, self.log.info, 0)
        threads = list(self.db.get_thread_details(parsed_args.run_id))
        if len(threads) > 1:
            for thread in threads:
                td = {
                    'id': thread.id,
                    'start_time': thread.start_time.isoformat(),
                    'end_time': thread.end_time.isoformat(),
                }
                output.dump_dictionary(td, self.log.info, 0)
        return
