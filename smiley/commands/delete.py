import logging

from cliff import command

from smiley import db


class Delete(command.Command):
    """Delete a run from the database

    """
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)
        parser.add_argument(
            '--database',
            default='smiley.db',
            help='filename for the database (%(default)s)',
        )
        parser.add_argument(
            'run_id',
            help='identifier for the run',
        )
        return parser

    def take_action(self, parsed_args):
        db_ = db.DB(parsed_args.database)
        try:
            db_.delete_run(parsed_args.run_id)
            self.log.info(u"Deleted run {}".format(parsed_args.run_id))
        except db.NoSuchRun:
            self.log.warn(u"No run found with id '{}' delete failed".format(
                parsed_args.run_id))
