import linecache
import logging
import os

from smiley.commands import listen_cmd
from smiley import output


class Monitor(listen_cmd.ListeningCommand):
    """Listen for running programs and show their progress.
    """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Monitor, self).get_parser(prog_name)
        parser.add_argument(
            '--exit',
            default=False,
            action='store_true',
            help='Exit monitor when sender exits',
        )
        return parser

    def take_action(self, parsed_args):
        self.out = output.OutputFormatter(linecache.getline)
        super(Monitor, self).take_action(parsed_args)

    def _process_message(self, msg):
        msg_type, msg_payload = msg
        self.log.debug('MESSAGE: %s %r', msg_type, msg_payload)

        if msg_type == 'start_run':
            self.out.start_run(
                msg_payload['run_id'],
                os.getcwd(),
                msg_payload['command_line'],
                msg_payload['timestamp'],
            )

        elif msg_type == 'end_run':
            self.out.end_run(
                msg_payload['run_id'],
                msg_payload['timestamp'],
                msg_payload['message'],
                msg_payload['traceback'],
            )
            if self._parsed_args.exit:
                raise SystemExit()

        else:
            self.out.trace(
                msg_payload['run_id'],
                msg_type,
                msg_payload['func_name'],
                msg_payload['line_no'],
                msg_payload['filename'],
                msg_payload['arg'],
                msg_payload['local_vars'],
                msg_payload['timestamp'],
            )
