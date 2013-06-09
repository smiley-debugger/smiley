import logging
from wsgiref import simple_server

from cliff import command

from pecan import configuration
from pecan import load_app

from smiley.web import config as config_module


class Server(command.Command):
    """Run the web server

    """

    log = logging.getLogger(__name__)

    _cwd = None

    def get_parser(self, prog_name):
        parser = super(Server, self).get_parser(prog_name)
        parser.add_argument(
            '--database',
            default='smiley.db',
            help='filename for the database (%(default)s)',
        )
        return parser

    def take_action(self, parsed_args):
        config_data = dict(vars(config_module).items())
        config_data['smiley'] = {
            'database_name': parsed_args.database,
        }
        app = load_app(config_data)

        # FIXME: Provide command line options to override these
        host = config_data['server']['host']
        port = int(config_data['server']['port'])
        srv = simple_server.make_server(host, port, app)
        if host == '0.0.0.0':
            self.log.info(
                'serving on 0.0.0.0:%s, view at http://127.0.0.1:%s',
                port, port,
            )
        else:
            self.log.info("serving on http://%s:%s", host, port)
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            # allow CTRL+C to shutdown
            pass
