create table run (
    id text primary key not null,
    cwd text,
    description text,  -- command line or other descriptive argument data
    start_time int,  -- timestamps as time.time() values
    end_time int,

    -- error handling
    error_message text,
    traceback text
);

create index if not exists run_id_idx on run (id);

create table trace (
    id integer primary key autoincrement not null,
    run_id text not null references run(id),
    
    event text not null,  -- the type of event that happened

    -- where the event happened
    filename text,
    line_no int,
    func_name text,
    trace_arg text,  -- the "arg" argument to the trace function, json-encoded
    locals text,  -- json-encoded dict
    timestamp int
);

create index if not exists trace_run_id_idx on trace (run_id);
