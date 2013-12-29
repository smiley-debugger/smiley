import logging
import os
import sys

from cliff import command

from smiley import local
from smiley import publisher
from smiley import tracer


class Run(command.Command):
    """Run another program with monitoring enabled.
    """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Run, self).get_parser(prog_name)
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '--local',
            action='store_const',
            dest='mode',
            const='local',
            help='write data to a local database',
        )
        group.add_argument(
            '--remote',
            action='store_const',
            dest='mode',
            const='remote',
            default='remote',
            help='send data to the remote monitor (default)',
        )
        include_group = parser.add_argument_group('covering')
        include_group.add_argument(
            '--include-stdlib',
            action='store_true',
            default=False,
            help='trace into standard library modules',
        )
        include_group.add_argument(
            '--no-include-stdlib',
            action='store_false',
            help='trace into standard library modules (default)',
        )
        include_group.add_argument(
            '--include-site-packages',
            action='store_true',
            default=True,
            help='trace into modules from site-packages (default)',
        )
        include_group.add_argument(
            '--no-include-site-packages',
            action='store_false',
            help='skip modules from site-packages',
        )
        include_group.add_argument(
            '--include-package',
            action='append',
            dest='include_packages',
            default=[],
            help='trace into a specific package',
        )
        parser.add_argument(
            '--database',
            default='smiley.db',
            help='filename for the database (%(default)s)',
        )
        parser.add_argument(
            '--socket',
            default='tcp://127.0.0.1:5556',
            help='URL for the socket where the listener will be (%(default)s)',
        )
        parser.add_argument(
            'command',
            nargs='+',
            help='the command to spy on',
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
        if parsed_args.mode == 'remote':
            p = publisher.Publisher(parsed_args.socket)
        else:
            p = local.LocalPublisher(parsed_args.database)
        t = tracer.Tracer(
            p,
            include_stdlib=parsed_args.include_stdlib,
            include_site_packages=parsed_args.include_site_packages,
            include_packages=parsed_args.include_packages,
        )
        t.run(parsed_args.command)
        return
