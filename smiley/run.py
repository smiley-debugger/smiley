import logging
import os
import sys

from cliff import command

from smiley import publisher, tracer


class Run(command.Command):
    """Run another program with monitoring enabled.
    """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Run, self).get_parser(prog_name)
        parser.add_argument(
            'command',
            nargs='+',
            help='the command to spy on',
        )
        parser.add_argument(
            '--socket',
            default='tcp://127.0.0.1:5556',
            help='URL for the socket where the listener will be (%(default)s)',
        )
        return parser

    def take_action(self, parsed_args):
        # Fix import path
        cwd = os.getcwd()
        if cwd not in sys.path and os.curdir not in sys.path:
            sys.path.insert(0, cwd)

        # Fix command line args
        sys.argv = parsed_args.command

        # Run the app
        p = publisher.Publisher(parsed_args.socket)
        t = tracer.Tracer(p)
        t.run(parsed_args.command)
        return
