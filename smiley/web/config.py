import os

from smiley import web

_web_pkg_dir = os.path.dirname(web.__file__)


def get_config_dict(database_name):
    return {

        # Server Specific Configurations
        'server': {
            'port': '8080',
            'host': '0.0.0.0'
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
    }
