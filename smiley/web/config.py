import os

from smiley import web

_web_pkg_dir = os.path.dirname(web.__file__)


def get_config_dict(database_name, host, port):
    return {

        # Server Specific Configurations
        'server': {
            'port': port,
            'host': host,
        },

        # Pecan Application Configurations
        'app': {
            'root': 'smiley.web.controllers.root.RootController',
            'modules': ['smiley.web'],
            'static_root': os.path.join(_web_pkg_dir, 'public'),
            'template_path': os.path.join(_web_pkg_dir, 'templates'),
            'debug': True,
            'errors': {
                404: '/error/404',
                '__force_dict__': True
            },
        },

        'smiley': {
            'database_name': database_name,
        },

        'beaker': {
            'session.type': 'cookie',
            'session.cookie_expires': True,
            'session.key': 'sessionkey',
            'session.validate_key': 'cbdd663a-48f2-481c-b207-f9775af33d12',
            '__force_dict__': True,
        },
    }
