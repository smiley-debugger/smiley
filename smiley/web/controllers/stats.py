import functools
import logging
import subprocess
import tempfile

from pecan import expose, request

from smiley.web import nav

LOG = logging.getLogger(__name__)


class StatsController(object):

    @expose(generic=True, template='stats.html')
    @nav.active_section('runs', 'stats')
    def index(self, run_id):
        run = request.db.get_run(run_id)

        def stats_data(stats):
            # FIXME(dhellmann): Don't hard-code the sort order
            stats.sort_stats('cumtime')
            ignored, func_list = stats.get_print_list(())
            for func in func_list:
                cc, nc, tt, ct, callers = stats.stats[func]
                yield {
                    'ncalls': '%s/%s' % (nc, cc) if nc != cc else str(nc),
                    'tottime': tt,
                    'percall_nc': (float(tt)/nc) if nc else '',
                    'cumtime': ct,
                    'percall_cc': (float(ct)/cc) if cc else '',
                    'filename': func[0],
                    'file_url': request.db.get_file_signature(run_id, func[0]),
                    'lineno': func[1],
                    'function': func[2],
                }

        return {
            'run_id': run_id,
            'run': run,
            'stats_data': stats_data(run.stats),
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
