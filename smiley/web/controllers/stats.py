import functools
import logging
import subprocess
import tempfile

from pecan import expose, request

from smiley.web import nav
from smiley.presentation import stats

LOG = logging.getLogger(__name__)


class StatsController(object):

    @expose(generic=True, template='stats.html')
    @nav.active_section('runs', 'stats')
    def index(self, run_id):
        run = request.db.get_run(run_id)
        return {
            'run_id': run_id,
            'run': run,
            'stats_data': stats.format_data(run_id, run.stats, request.db),
            'getfileid': functools.partial(request.db.get_file_signature,
                                           run_id=run_id),
        }

    @expose(generic=True, template='graph.html')
    @nav.active_section('runs', 'graph')
    def graph(self, run_id):
        run = request.db.get_run(run_id)
        return {
            'run_id': run_id,
            'run': run,
        }

    @expose(content_type='image/png')
    @nav.active_section('runs', 'graph')
    def graph_data(self, run_id):
        run = request.db.get_run(run_id)
        try:
            with tempfile.NamedTemporaryFile(mode='w') as f:
                run.stats.dump_stats(f.name)
                image_data = subprocess.check_output(
                    'gprof2dot -f pstats %s | dot -Tpng' % f.name,
                    shell=True,
                )
        except:
            LOG.exception('could not generate image')
            raise
        return image_data
