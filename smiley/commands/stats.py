import logging
import pstats

from cliff import command

from smiley import db


class StatsShow(command.Command):
    """Show the profile output for a run

    """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(StatsShow, self).get_parser(prog_name)
        parser.add_argument(
            '--database',
            default='smiley.db',
            help='filename for the database (%(default)s)',
        )
        parser.add_argument(
            '--sort-order',
            default='cumulative',
            choices=list(sorted(pstats.Stats.sort_arg_dict_default.keys())),
        )
        parser.add_argument(
            'run_id',
            help='identifier for the run',
        )
        return parser

    def take_action(self, parsed_args):
        self.db = db.DB(parsed_args.database)
        run_details = self.db.get_run(parsed_args.run_id)
        if not run_details.stats:
            print 'No profiling data was collected'
        else:
            run_details.stats.sort_stats(parsed_args.sort_order)
            run_details.stats.print_stats()


class StatsExport(command.Command):
    """Write the profile output for a run to a file

    """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(StatsExport, self).get_parser(prog_name)
        parser.add_argument(
            '--database',
            default='smiley.db',
            help='filename for the database (%(default)s)',
        )
        parser.add_argument(
            'run_id',
            help='identifier for the run',
        )
        parser.add_argument(
            'filename',
            help='the name of the file to use for the data',
        )
        return parser

    def take_action(self, parsed_args):
        self.db = db.DB(parsed_args.database)
        run_details = self.db.get_run(parsed_args.run_id)
        run_details.stats.dump_stats(parsed_args.filename)
