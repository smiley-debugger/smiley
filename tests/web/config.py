# Server Specific Configurations
server = {
    'port': '8080',
    'host': '0.0.0.0'
}

import os
from smiley import web
web_pkg_dir = os.path.dirname(web.__file__)
del web
del os

# Pecan Application Configurations
app = {
    'root': 'smiley.web.controllers.root.RootController',
    'modules': ['smiley.web'],
    'static_root': web_pkg_dir + '/public',
    'template_path': web_pkg_dir + '/templates',
    'debug': True,
    'errors': {
        '404': '/error/404',
        '__force_dict__': True
    }
}

# Custom Configurations must be in Python dictionary format::
#
# foo = {'bar':'baz'}
#
# All configurations are accessible at::
# pecan.conf
