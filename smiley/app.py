import logging
import sys

from cliff import app
from cliff import commandmanager

import pkg_resources


class Smiley(app.App):

    log = logging.getLogger(__name__)

    def __init__(self):
        dist = pkg_resources.get_distribution('smiley')
        super(Smiley, self).__init__(
            description='smiley spies on your apps as they run',
            version=dist.version,
            command_manager=commandmanager.CommandManager('smiley.commands'),
        )


def main(argv=sys.argv[1:]):
    return Smiley().run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
