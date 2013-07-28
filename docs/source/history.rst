=================
 Release History
=================

0.5
===

- Add a call graph image, built with gprof2dot_ and graphviz_.

- Add :doc:`server` documentation.
- Clean up template implementations.
- Clean up navigation and breadcrumbs.

.. _gprof2dot: https://code.google.com/p/jrfonseca/wiki/Gprof2Dot
.. _graphviz: http://www.graphviz.org/

0.4
===

- Collect profiling data along with the trace data.
- Add :ref:`command-stats-show` command.
- Add :ref:`command-stats-export` command.

0.3
===

- Add :ref:`command-record` command.
- Add :ref:`command-list` command.
- Add web ui and :ref:`command-server` command
- Add mode option to :ref:`command-run` to allow writing results
  directly to a database file.

0.2
===

Use the script runner code from coverage_ instead of reinventing it.

.. _coverage: https://pypi.python.org/pypi/coverage

0.1
===

First public release. Includes basic functionality of runner and
monitor.
