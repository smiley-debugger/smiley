create table run (
    id text primary key not null,
    cwd text,
    description text,  -- command line or other descriptive argument data
    start_time int,  -- timestamps as time.time() values
    end_time int,

    -- error handling
    error_message text,
    traceback text,

    -- performance data
    stats text
);

create index if not exists run_id_idx on run (id);

create table trace (
    id integer primary key autoincrement not null,
    run_id text not null references run(id),

    thread_id text, -- separate calls from different threads
    call_id text, -- might be null for code outside a function

    event text not null,  -- the type of event that happened

    -- where the event happened
    filename text,
    line_no int,
    func_name text,
    trace_arg text,  -- the "arg" argument to the trace function, json-encoded
    local_vars text,  -- json-encoded dict
    timestamp int
);

-- a view to help produce the counts of the unique locations executed by a thread
CREATE VIEW IF NOT EXISTS location_counts AS
SELECT run_id, thread_id, COUNT(*) as num_locations
FROM (SELECT DISTINCT run_id, thread_id, filename,
      line_no AS location
      FROM trace)
GROUP BY run_id, thread_id
;


create index if not exists trace_run_id_idx on trace (run_id);

create table file (
    signature text primary key not null,
    name text,
    body text
);

create unique index
    if not exists file_signature_name_idx
    on file(signature, name);

create table run_file (
    run_id text not null references run(id),
    signature text not null references file(signature)
);

create unique index
    if not exists run_file_id_signature_idx
    on run_file(run_id, signature);
