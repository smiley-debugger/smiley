import itertools
import linecache
import logging
import os
import pprint
import sys

import prettytable

from smiley.commands import listen_cmd


def dump_dictionary(d, stdout, indent=4):
    x = prettytable.PrettyTable(field_names=('Variable', 'Value'),
                                print_empty=False)
    x.padding_width = 1
    # Align all columns left because the values are
    # not all the same type.
    x.align['Variable'] = 'l'
    x.align['Value'] = 'l'
    for name, value in sorted(d.items()):
        formatted_value = pprint.pformat(value, width=60)
        pairs = itertools.izip(
            itertools.chain([name], itertools.repeat('')),
            formatted_value.splitlines())
        for name, value in pairs:
            x.add_row((name, value))
    formatted = x.get_string(fields=('Variable', 'Value'))
    indent_spaces = ' ' * 4
    for line in formatted.splitlines():
        stdout.write(indent_spaces + line + '\n')
    return


class Monitor(listen_cmd.ListeningCommand):
    """Listen for running programs and show their progress.
    """

    log = logging.getLogger(__name__)

    _cwd = None

    def get_parser(self, prog_name):
        parser = super(Monitor, self).get_parser(prog_name)
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
            if msg_payload.get('message'):
                self.log.info(
                    'ERROR in app: %s',
                    msg_payload.get('message', msg_payload),
                )
            if self._parsed_args.exit:
                raise SystemExit()

        else:
            filename = msg_payload['filename']
            if self._cwd and filename.startswith(self._cwd):
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
            elif msg_type == 'exception':
                self.log.info(
                    '%s:%4s: Exception:',
                    filename,
                    msg_payload['line_no'],
                )
                exc_type, exc_msg, exc_tb = msg_payload['arg']
                for exc_file, exc_line, exc_func, exc_text in exc_tb:
                    self.log.info(
                        '    %s:%4s: %s',
                        exc_file, exc_line, exc_text,
                    )
            else:
                self.log.info(
                    '%s:%4s: %s',
                    filename,
                    msg_payload['line_no'],
                    line,
                )
                if msg_payload.get('locals'):
                    dump_dictionary(msg_payload['locals'], sys.stdout)
