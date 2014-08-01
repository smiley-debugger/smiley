

def get_context(db, run_id, thread_id):
    return {
        'run_id': run_id,
        'run': db.get_run(run_id),
        'thread_id': thread_id,
        'thread_details': list(db.get_thread_details(run_id)),
    }
