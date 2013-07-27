===================
 Command Reference
===================

The main program for Smiley is ``smiley``. It includes several
sub-commands.

.. _command-run:

run
===

Run an application and trace its execution.

.. _command-monitor:

monitor
=======

Listen for trace data from an application running under the ``run``
command.

.. _command-record:

record
======

Listen for trace data from an application running under the ``run``
command and write it to a database for later analysis.

.. _command-list:

list
====

Show the runs previously recorded in the database.

.. _command-replay:

replay
======

Given a single run id, dump the data from that run in the same format
as the ``monitor`` command.

.. _command-server:

server
======

Run a web server for browsing the pre-recorded run data collected
by the ``record`` command.

.. _command-stats-show:

stats show
==========

Show the profiling data from a run.

.. _command-stats-export:

stats export
============

Dump the profiling data from a run to a local file.

.. _command-help:

help
====

Get help for the ``smiley`` command or a subcommand.
