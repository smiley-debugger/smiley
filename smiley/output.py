import itertools
import logging
import os
import pprint

import prettytable

from smiley import processor


def format_dictionary(d):
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
    return x.get_string(fields=('Variable', 'Value'))


def dump_table(formatted, write, indent=0):
    # Use the write function we're given, one line at a time.
    indent_spaces = ' ' * 4
    for line in formatted.splitlines():
        write(indent_spaces + line)
    return


def dump_dictionary(d, write, indent=4):
    dump_table(format_dictionary(d), write, indent)


class OutputFormatter(processor.EventProcessor):

    log = logging.getLogger(__name__)

    _cwd = None

    def __init__(self, line_source):
        self._line_source = line_source

    def _get_display_filename(self, filename):
        "Truncate the filename for display."
        if self._cwd and filename.startswith(self._cwd):
            return filename[len(self._cwd):]
        return filename

    def start_run(self, run_id, cwd, description, start_time):
        self.log.info(
            'Starting new run: %s',
            ' '.join(description)
        )
        self._cwd = cwd
        if self._cwd:
            self._cwd = self._cwd.rstrip(os.sep) + os.sep

    def end_run(self, run_id, end_time, message, traceback, stats):
        self.log.info('Finished run')
        if message:
            self.log.info('ERROR in app: %s', message)

    def trace(self, run_id, event,
              func_name, line_no, filename,
              trace_arg, local_vars,
              timestamp):
        line = self._line_source(
            filename,
            line_no,
        ).rstrip()
        display_filename = self._get_display_filename(filename)
        if event in ('line', 'call'):
            self.log.info(
                '%s:%4s: %s',
                display_filename,
                line_no,
                line,
            )
            if local_vars:
                dump_dictionary(local_vars, self.log.info)
        elif event == 'return':
            self.log.info(
                '%s:%4s: return>>> %s',
                display_filename,
                line_no,
                trace_arg,
            )
        elif event == 'exception':
            self.log.warn(
                '%s:%4s: Exception:',
                display_filename,
                line_no,
            )
            exc_type, exc_msg, exc_tb = trace_arg
            for exc_file, exc_line, exc_func, exc_text in exc_tb:
                self.log.info(
                    '    %s:%4s: %s',
                    self._get_display_filename(exc_file), exc_line, exc_text,
                )
        else:
            print 'UNHANDLED EVENT:', event
