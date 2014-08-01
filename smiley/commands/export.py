import logging
import time

from cliff import command

from smiley import db
from smiley import stats


class _ImportExportBase(command.Command):

    log = logging.getLogger(__name__)

    def _copy_run(self, input_name, output_name, run_id):
        input_db = db.DB(input_name)
        run = input_db.get_run(run_id)
        output_db = db.DB(output_name)
        start_time = time.mktime(run.start_time.timetuple())
        output_db.start_run(
            run_id,
            run.cwd,
            run.description,
            start_time,
        )
        self.log.debug('Copying trace data')
        for t in input_db.get_trace(run_id):
            timestamp = time.mktime(t.timestamp.timetuple())
            output_db.trace(
                t.run_id,
                t.call_id,
                t.event,
                t.func_name,
                t.line_no,
                t.filename,
                t.trace_arg,
                t.local_vars,
                timestamp,
            )
        for f_info in input_db.get_files_for_run(run_id):
            self.log.debug('Adding cached file %s', f_info.name)
            f_body = input_db.get_cached_file(run_id, f_info.name)
            output_db.cache_file_for_run(
                run_id,
                f_info.name,
                f_body,
            )
        end_time = time.mktime(run.end_time.timetuple())
        output_db.end_run(
            run_id=run_id,
            end_time=end_time,
            message=run.error_message,
            traceback=run.traceback,
            stats=stats.stats_to_blob(run.stats),
        )


class Export(_ImportExportBase):
    """Export the data from one run to a new database.
    """

    def get_parser(self, prog_name):
        parser = super(Export, self).get_parser(prog_name)
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
            'destination',
            nargs='?',
            help='filename for output, defaults to run_id + ".db"',
        )
        return parser

    def take_action(self, parsed_args):
        dest = parsed_args.destination
        if not dest:
            dest = parsed_args.run_id + '.db'
        self._copy_run(parsed_args.database, dest, parsed_args.run_id)
