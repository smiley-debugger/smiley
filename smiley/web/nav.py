import functools


def active_section(active_section_name, subsection=None):
    """Insert the active section name into the template context.
    """
    def set_active_section(f):
        @functools.wraps(f)
        def decorator(*args, **kwds):
            result = f(*args, **kwds)
            if isinstance(result, dict):
                result['active_section'] = active_section_name
                result['active_subsection'] = subsection
            return result
        return decorator
    return set_active_section
