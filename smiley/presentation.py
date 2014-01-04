import logging
import math

from smiley import db
from smiley import util

LOG = logging.getLogger(__name__)


def collapse_trace(trace_iter):
    """Combine closely related trace items.
    """
    accumulate = None
    for t in trace_iter:
        vars_have_changed = False
        if accumulate:
            vars_that_changed = util.get_variable_changes(
                accumulate.local_vars,
                t.local_vars,
            )
            for var, val in vars_that_changed:
                if var in accumulate.local_vars:
                    # The value of an existing variable changed between events
                    vars_have_changed = True
                    break
        do_yield = (
            accumulate  # we have something to yield
            and
            (vars_have_changed
             or
             accumulate.event != 'line'  # that something can't be collapsed
             or
             t.event != 'line'  # the next event can't be combined with it
             or
             t.event != accumulate.event)
        )
        if do_yield:
            # The events do not match or can't be combined
            yield accumulate
            accumulate = None

        if not accumulate:
            accumulate = db.Trace(
                id=t.id,
                run_id=t.run_id,
                call_id=t.call_id,
                event=t.event,
                filename=t.filename,
                line_no=(t.line_no, t.line_no),
                func_name=t.func_name,
                trace_arg=t.trace_arg,
                local_vars=t.local_vars,
                timestamp=t.timestamp,
            )

        else:
            # Combine consecutive line events by updating the line_no
            # range
            accumulate = db.Trace(
                id=accumulate.id,
                run_id=accumulate.run_id,
                call_id=accumulate.call_id,
                event=accumulate.event,
                filename=accumulate.filename,
                line_no=(accumulate.line_no[0], t.line_no),
                func_name=accumulate.func_name,
                trace_arg=accumulate.trace_arg,
                # replace in case variables were added
                local_vars=t.local_vars,
                timestamp=accumulate.timestamp,
            )

    if accumulate:
        yield accumulate


def _bounded_int(val, default, low, high):
    try:
        val = int(val)
    except (TypeError, ValueError):
        val = default
    else:
        val = min(val, high)
        val = max(val, low)
    return val


def get_pagination_values(page, per_page, num_items):
    per_page = _bounded_int(per_page, 20, 5, 100)
    num_pages = int(math.ceil(num_items / (per_page * 1.0)))
    page = _bounded_int(page, 1, 1, num_pages)
    start = (page - 1) * per_page
    end = start + per_page

    # We don't want to show every page number, so figure out
    # the ranges we *do* want to show.
    page_ranges = []
    if num_pages <= 7:
        page_ranges.append((1, num_pages))
    elif page <= 5:
        page_ranges.append((1, 5))
        page_ranges.append((num_pages, num_pages))
    elif page >= num_pages - 5 + 1:
        page_ranges.append((1, 1))
        page_ranges.append((num_pages - 5 + 1, num_pages))
    else:
        page_ranges.append((1, 1))
        page_ranges.append((page - 2, page + 2))
        page_ranges.append((num_pages, num_pages))

    return {
        'page': page,
        'per_page': per_page,
        'num_pages': num_pages,
        'start': start,
        'end': end,
        'page_ranges': page_ranges,
    }
