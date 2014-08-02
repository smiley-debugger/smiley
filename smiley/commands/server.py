import logging
from wsgiref import simple_server

from beaker.middleware import SessionMiddleware
from cliff import command
from pecan import load_app
import six

from smiley.web import config as web_config


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
        parser.add_argument(
            '--host',
            default='0.0.0.0',
            help='IP on which to listen (%(default)s)',
        )
        parser.add_argument(
            '--port',
            default=8080,
            type=int,
            help='port on which to listen (%(default)s)',
        )
        return parser

    def take_action(self, parsed_args):
        config_data = web_config.get_config_dict(
            database_name=parsed_args.database,
            host=parsed_args.host,
            port=parsed_args.port,
        )
        app = load_app(config_data)

        # Add beaker session middleware so we can track where the user
        # is and navigate back to the same place as they change tabs.
        if six.PY2:
            app = SessionMiddleware(app, config_data['beaker'])

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
