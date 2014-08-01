import logging

from cliff import lister

from smiley import db


class Threads(lister.Lister):
    """Show the details from the threads of one run.
    """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Threads, self).get_parser(prog_name)
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
        threads = list(self.db.get_thread_details(parsed_args.run_id))
        # for thread in threads:
        #     td = {
        #         'id': thread.id,
        #         'start_time': thread.start_time.ctime(),
        #         'end_time': thread.end_time.ctime(),
        #     }
        #     output.dump_dictionary(td, self.log.info, 0)
        return (('ID', 'Start', 'End'), threads)
