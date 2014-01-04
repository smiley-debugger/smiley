def format_data(run_id, stats, db):
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
            'file_url': db.get_file_signature(run_id, func[0]),
            'lineno': func[1],
            'function': func[2],
        }
