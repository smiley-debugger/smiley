import linecache
import logging
import os

from cliff import command

from smiley import db
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

    def _process_message(self, msg):
        msg_type, msg_payload = msg
        self.log.debug('MESSAGE: %s %r', msg_type, msg_payload)

        # TODO: Make sure the file appears in our cache.
        #       - use a simple hash signature
        #       - assume unique for life of a "run"

        # filename = msg_payload['filename']
        # if filename.startswith(self._cwd):
        #     filename = filename[len(self._cwd):]
        # line = linecache.getline(
        #     msg_payload['filename'],  # use the full name here
        #     msg_payload['line_no'],
        # ).rstrip()

        if msg_type == 'start_run':
            command_line = ' '.join(msg_payload.get('command_line', []))
            self.log.info(
                'Starting new run: %s',
                command_line,
            )
            self._cwd = msg_payload.get('cwd', '')
            if self._cwd:
                self._cwd = self._cwd.rstrip(os.sep) + os.sep
            self.db.start_run(
                run_id=msg_payload['run_id'],
                cwd=self._cwd,
                description=command_line,
                start_time=msg_payload.get('timestamp'),
            )

        elif msg_type == 'end_run':
            self.log.info('Finished run')
            self.db.end_run(
                run_id=msg_payload['run_id'],
                end_time=msg_payload.get('timestamp'),
                message=msg_payload.get('message'),
                traceback=msg_payload.get('traceback'),
            )

        else:
            self.db.trace(
                run_id=msg_payload['run_id'],
                event=msg_type,
                func_name=msg_payload.get('func_name'),
                line_no=msg_payload.get('line_no'),
                filename=msg_payload.get('filename'),
                trace_arg=msg_payload.get('arg'),
                local_vars=msg_payload.get('local_vars'),
                timestamp=msg_payload.get('timestamp'),
            )

    def take_action(self, parsed_args):
        self.out = output.OutputFormatter(linecache.getline)
        self.db = db.DB(parsed_args.database)

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
