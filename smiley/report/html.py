import functools
import logging
import os
import shutil

from mako.lookup import TemplateLookup

from smiley import db_linecache
from smiley.presentation import pagination
from smiley.presentation import stats
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
            'getfileid': functools.partial(
                report.db.get_file_signature,
                run_id=report.run_id,
            ),
        }
        if self.TEMPLATE:
            self.template = report.template_lookup.get_template(self.TEMPLATE)
            self.context['active_section'] = self.TEMPLATE.partition('.')[0]
        else:
            self.template = None
            self.context['active_section'] = None

    def render(self):
        return self.template.render_unicode(**self.context)


class IndexPage(Page):
    TEMPLATE = 'index.html'

    def __init__(self, report):
        super(IndexPage, self).__init__(report)


class TracePage(Page):
    TEMPLATE = 'trace.html'

    def __init__(self, report, trace, pagination, getlines):
        super(TracePage, self).__init__(report)
        self.context['trace'] = trace
        self.context.update(pagination)
        self.context['getlines'] = getlines


class FilesPage(Page):
    TEMPLATE = 'files.html'

    def __init__(self, report, files):
        super(FilesPage, self).__init__(report)
        self.context['files'] = files


class FilePage(Page):
    TEMPLATE = 'file.html'

    def __init__(self, report, file_info):
        super(FilePage, self).__init__(report)
        self.context['active_section'] = 'files'
        filename, body = report.db.get_cached_file_by_id(
            report.run_id,
            file_info.signature,
        )
        self.context['styled_body'] = syntax.apply_style(filename, body)


class StatsPage(Page):
    TEMPLATE = 'stats.html'

    def __init__(self, report):
        super(StatsPage, self).__init__(report)
        self.context['stats_data'] = stats.format_data(
            report.run_id,
            report.run_details.stats,
            report.db,
        )


class CallGraphPage(Page):
    TEMPLATE = 'call_graph.html'

    def __init__(self, report):
        super(CallGraphPage, self).__init__(report)
        self.stats_data = report.run_details.stats
        self.image_filename = os.path.join(report.output_dir, 'call_graph.png')

    def render(self):
        image_data = stats.generate_call_graph(self.stats_data)
        with open(self.image_filename, 'w') as f:
            f.write(image_data)
        return super(CallGraphPage, self).render()


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

    def run(self):
        LOG.info('writing output to %s', self.output_dir)

        # Do some initial calculations to figure out how many pages we
        # have.
        trace_data = list(
            trace.collapse_trace(self.db.get_trace(self.run_id))
        )
        page_vals = pagination.get_pagination_values(
            1, self.per_page, len(trace_data),
        )
        last_page = page_vals['num_pages'] + 1

        # Start producing output pages
        self._render_page(
            IndexPage(
                report=self,
            ),
            'index.html',
        )

        # The trace output is paginated, so we have multiple pages to
        # produce.
        for i in range(1, last_page):
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

        # The source code from the run
        run_files = list(self.db.get_files_for_run(self.run_id))
        self._render_page(
            FilesPage(self, run_files),
            'files.html',
        )
        for run_file in run_files:
            self._render_page(
                FilePage(self, run_file),
                'file-%s.html' % run_file.signature,
            )

        self._render_page(
            StatsPage(self),
            'stats.html',
        )
        self._render_page(
            CallGraphPage(self),
            'call_graph.html',
        )

        # Make sure we have all of the CSS and JavaScript files needed
        # by the templates.
        self._copy_static_files()
