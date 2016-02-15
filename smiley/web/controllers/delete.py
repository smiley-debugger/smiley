import logging

from pecan import expose, redirect, request

LOG = logging.getLogger(__name__)

class DeleteController(object):

    @expose(generic=True)
    def index(self, run_id):
        """Delete a run and redirect to the list of runs"""
        if run_id:
            request.db.delete_run(run_id)
        redirect("/runs")
