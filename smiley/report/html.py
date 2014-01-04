import functools
import logging
import os
import shutil

from mako.lookup import TemplateLookup

from smiley import db_linecache
from smiley.presentation import pagination
from smiley.presentation import trace
from smiley.presentation import syntax


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


class TracePage(Page):
    TEMPLATE = 'trace.html'

    def __init__(self, report, trace, pagination, getlines):
        super(TracePage, self).__init__(report)
        self.context['trace'] = trace
        self.context.update(pagination)
        self.context['getlines'] = getlines
        self.context['getfileid'] = functools.partial(
            report.db.get_file_signature,
            run_id=report.run_id,
        )


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
        self.syntax_line_cache = syntax.StyledLineCache(self.db, self.run_id)

    def _render_page(self, page, output_name):
        fullname = os.path.join(self.output_dir, output_name)
        outdir = os.path.dirname(fullname)
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        with open(fullname, 'w') as f:
            LOG.info('writing %s', output_name)
            f.write(page.render().encode('utf-8', 'replace'))

    def _get_file_lines(self, filename, nums):
        start, end = nums
        return self.syntax_line_cache.getlines(
            filename, start, end,
            include_comments=True,
        )

    def run(self):
        LOG.info('writing output to %s', self.output_dir)

        self._render_page(IndexPage(self), 'index.html')

        trace_data = list(
            trace.collapse_trace(self.db.get_trace(self.run_id))
        )
        page_vals = pagination.get_pagination_values(
            1, self.per_page, len(trace_data),
        )
        last_page = page_vals['num_pages'] + 1
        for i in xrange(1, last_page):
            page_vals = pagination.get_pagination_values(
                i, self.per_page, len(trace_data),
            )
            page_name = 'trace-%d.html' % i
            start = page_vals['start']
            end = page_vals['end']
            self._render_page(
                TracePage(
                    report=self,
                    trace=trace_data[start:end],
                    pagination=page_vals,
                    getlines=self._get_file_lines,
                ),
                page_name,
            )

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
