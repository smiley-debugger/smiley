import abc
import logging

from cliff import command

from smiley import listener


class ListeningCommand(command.Command):
    """Base class for commands that listen for messages from the runner.
    """

    __metaclass__ = abc.ABCMeta

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(ListeningCommand, self).get_parser(prog_name)
        parser.add_argument(
            '--socket',
            dest='socket',
            default='tcp://127.0.0.1:5556',
            help='URL for the socket where to monitor on (%(default)s)',
        )
        return parser

    @abc.abstractmethod
    def _process_message(self, msg):
        msg_type, msg_payload = msg
        self.log.debug('MESSAGE: %s %r', msg_type, msg_payload)
        return

    def take_action(self, parsed_args):
        self._parsed_args = parsed_args
        l = listener.Listener(parsed_args.socket)
        l.poll_forever(self._process_message)
        return
