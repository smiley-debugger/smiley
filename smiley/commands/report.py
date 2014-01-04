import logging

from cliff import command

from smiley import db
from smiley.report import html


class Report(command.Command):
    """Create an HTML report for a previously captured run.

    """

    log = logging.getLogger(__name__)

    _cwd = None

    def get_parser(self, prog_name):
        parser = super(Report, self).get_parser(prog_name)
        parser.add_argument(
            '--database',
            default='smiley.db',
            help='filename for the database (%(default)s)',
        )
        parser.add_argument(
            '--items-per-page',
            default=100,
            type=int,
            help='steps of execution shown on a page (%(default)s)',
        )
        parser.add_argument(
            '-o', '--output-directory',
            default=None,
            help='location of the output ($run_id)',
        )
        parser.add_argument(
            '--title',
            default='',
            help='title for the report',
        )
        parser.add_argument(
            'run_id',
            help='identifier for the run',
        )
        return parser

    def take_action(self, parsed_args):
        database = db.DB(parsed_args.database)
        output_dir = parsed_args.output_directory or parsed_args.run_id
        report = html.HTMLReport(
            run_id=parsed_args.run_id,
            output_dir=output_dir,
            database=database,
            title=parsed_args.title or parsed_args.run_id,
            per_page=parsed_args.items_per_page,
        )
        report.run()
