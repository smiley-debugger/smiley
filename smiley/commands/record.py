import logging

from smiley import local
from smiley.commands import listen_cmd


class Record(listen_cmd.ListeningCommand):
    """Listen for running programs and record the data to a database for
    later use.

    """

    log = logging.getLogger(__name__)

    _cwd = None

    def get_parser(self, prog_name):
        parser = super(Record, self).get_parser(prog_name)
        parser.add_argument(
            '--database',
            default='smiley.db',
            help='filename for the database (%(default)s)',
        )
        return parser

    def _process_message(self, msg):
        msg_type, msg_payload = msg
        self.log.debug('MESSAGE: %s %r', msg_type, msg_payload)

        if msg_type == 'start_run':
            command_line = ' '.join(msg_payload.get('command_line', []))
            self.log.info(
                'Starting new run: %s',
                command_line,
            )
            self.publisher.start_run(
                run_id=msg_payload['run_id'],
                cwd=self._cwd,
                description=msg_payload.get('command_line', []),
                start_time=msg_payload.get('timestamp'),
            )

        elif msg_type == 'end_run':
            self.log.info('Finished run')
            self.publisher.end_run(
                run_id=msg_payload['run_id'],
                end_time=msg_payload.get('timestamp'),
                message=msg_payload.get('message'),
                traceback=msg_payload.get('traceback'),
            )

        else:
            self.publisher.trace(
                run_id=msg_payload['run_id'],
                call_id=msg_payload['call_id'],
                event=msg_type,
                func_name=msg_payload.get('func_name'),
                line_no=msg_payload.get('line_no'),
                filename=msg_payload.get('filename'),
                trace_arg=msg_payload.get('arg'),
                local_vars=msg_payload.get('local_vars'),
                timestamp=msg_payload.get('timestamp'),
            )

    def take_action(self, parsed_args):
        self.publisher = local.LocalPublisher(parsed_args.database)
        return super(Record, self).take_action(parsed_args)
