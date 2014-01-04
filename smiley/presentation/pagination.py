import math


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
