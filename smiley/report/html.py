import logging
import os
import shutil

from mako.lookup import TemplateLookup

from smiley import db_linecache


LOG = logging.getLogger(__name__)


class Page(object):

    TEMPLATE = None

    def __init__(self, report):
        self.context = {
            'subtitle': report.title,
            'run_id': report.run_id,
            'run': report.run_details,
        }
        if self.TEMPLATE:
            self.template = report.template_lookup.get_template(self.TEMPLATE)
        else:
            self.template = None

    def render(self):
        return self.template.render_unicode(**self.context)


class IndexPage(Page):

    TEMPLATE = 'index.html'


class HTMLReport(object):

    def __init__(self, run_id, output_dir, database, title, per_page):
        self.run_id = run_id
        self.output_dir = output_dir
        self.db = database
        self.title = title
        self.per_page = per_page

        self.run_details = self.db.get_run(self.run_id)
        self.line_cache = db_linecache.DBLineCache(self.db, self.run_id)
        self.report_dir = os.path.dirname(__file__)
        self.template_dir = os.path.join(self.report_dir, 'templates')
        self.template_lookup = TemplateLookup(directories=[self.template_dir])

    def _render_page(self, page, output_name):
        fullname = os.path.join(self.output_dir, output_name)
        outdir = os.path.dirname(fullname)
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        with open(fullname, 'w') as f:
            LOG.info('writing %s', output_name)
            f.write(page.render().encode('utf-8', 'replace'))

    def run(self):
        LOG.info('writing output to %s', self.output_dir)

        self._render_page(IndexPage(self), 'index.html')
        self._copy_static_files()

        # [ ] index.html to show basic details and link to the trace,
        #     files, stats, and call graph pages
        # [ ] trace 1..n pages
        # [ ] file list page
        # [ ] file contents page(s)
        # [ ] stats page
        # [ ] call graph page
        # [ ] call graph image
        # [x] copy static files

        # self.out.start_run(
        #     run_details.id,
        #     run_details.cwd,
        #     run_details.description,
        #     run_details.start_time,
        # )
        # for t in self.db.get_trace(parsed_args.run_id):
        #     self.out.trace(
        #         t.run_id,
        #         t.event,
        #         t.func_name,
        #         t.line_no,
        #         t.filename,
        #         t.trace_arg,
        #         t.local_vars,
        #         t.timestamp,
        #     )
        # self.out.end_run(
        #     run_details.id,
        #     run_details.end_time,
        #     run_details.error_message,
        #     None,  # run_details.traceback,
        # )

    def _copy_static_files(self):
        static_dir = os.path.join(self.report_dir, 'static')
        for in_dir in os.listdir(static_dir):
            src = os.path.join(static_dir, in_dir)
            dst = os.path.join(self.output_dir, in_dir)
            if os.path.exists(dst):
                LOG.debug('cleaning up %s', dst)
                shutil.rmtree(dst)
            LOG.info('copying static files: %s', in_dir)
            shutil.copytree(src, dst)
