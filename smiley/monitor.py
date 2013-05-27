import linecache
import logging
import os

from cliff import command

from smiley import listener


class Monitor(command.Command):
    """Listen for running programs and show their progress.
    """

    log = logging.getLogger(__name__)

    _cwd = None

    def get_parser(self, prog_name):
        parser = super(Monitor, self).get_parser(prog_name)
        parser.add_argument(
            '--socket',
            dest='socket',
            default='tcp://127.0.0.1:5556',
            help='URL for the socket where to monitor on (%(default)s)',
        )
        parser.add_argument(
            '--exit',
            default=False,
            action='store_true',
            help='Exit monitor when sender exits',
        )
        return parser

    def _process_message(self, msg):
        msg_type, msg_payload = msg
        self.log.debug('MESSAGE: %s %r', msg_type, msg_payload)

        if msg_type == 'start_run':
            self.log.info(
                'Starting new run: %s',
                ' '.join(msg_payload.get('command_line', []))
            )
            self._cwd = msg_payload.get('cwd', '')
            if self._cwd:
                self._cwd = self._cwd.rstrip(os.sep) + os.sep

        elif msg_type == 'end_run':
            self.log.info('Finished run')
            if self._parsed_args.exit:
                raise SystemExit()

        elif msg_type == 'exception':
            # TODO: Report more details.
            self.log.info('ERROR in app: %s', msg_payload['message'])
            if self._parsed_args.exit:
                raise SystemExit()

        else:
            filename = msg_payload['filename']
            if filename.startswith(self._cwd):
                filename = filename[len(self._cwd):]
            line = linecache.getline(
                msg_payload['filename'],  # use the full name here
                msg_payload['line_no'],
            ).rstrip()
            if msg_type == 'return':
                self.log.info(
                    '%s:%4s: return>>> %s',
                    filename,
                    msg_payload['line_no'],
                    msg_payload['arg'],
                )
            else:
                self.log.info(
                    '%s:%4s: %s',
                    filename,
                    msg_payload['line_no'],
                    line,
                )
                if msg_payload.get('locals'):
                    for n, v in sorted(msg_payload['locals'].items()):
                        self.log.info(
                            '%s       %s = %s',
                            ' ' * len(filename),
                            n,
                            v,
                        )

    def take_action(self, parsed_args):
        self._parsed_args = parsed_args
        l = listener.Listener(parsed_args.socket)
        l.poll_forever(self._process_message)
        return
