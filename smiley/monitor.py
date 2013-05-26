import linecache
import logging

from cliff import command

from smiley import listener


class Monitor(command.Command):
    """Listen for running programs and show their progress.
    """

    log = logging.getLogger(__name__)

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
        print 'MESSAGE:', msg
        msg_type, msg_payload = msg
        if msg_type == 'start_run':
            print 'Starting new run:', msg_payload.get('command_line')
        elif msg_type == 'end_run':
            print 'Finished run'
            if self._parsed_args.exit:
                raise SystemExit()
        else:
            #print msg_type, msg_payload
            line = linecache.getline(
                msg_payload['filename'],
                msg_payload['line_no'],
            ).rstrip()
            if msg_type == 'return':
                print '%s:%4s: return>>> %s' % (
                    msg_payload['filename'],
                    msg_payload['line_no'],
                    msg_payload['arg'],
                )
            else:
                print '%s:%4s: %s' % (
                    msg_payload['filename'],
                    msg_payload['line_no'],
                    line,
                )
                if msg_payload.get('locals'):
                    for n, v in sorted(msg_payload['locals'].items()):
                        print '%s       %s = %s' % (
                            ' ' * len(msg_payload['filename']),
                            n,
                            v,
                        )
            print

    def take_action(self, parsed_args):
        self._parsed_args = parsed_args
        l = listener.Listener(parsed_args.socket)
        l.poll_forever(self._process_message)
        return
