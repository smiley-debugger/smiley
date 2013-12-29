=================
 Release History
=================

0.6
===

- Update the web view to only show changes in variables. The
  calculation of changes is very rough, and just compares the current
  set of variables to the previous set, which might be in a completely
  unrelated scope.
- Update the web view to show consecutive lines executed together as a
  single block. A new block is started for each call into a function
  or when the value of a previously-seen local variable changes.
- Update the web view to show comments near the source line being
  executed as further context.
- Simplify calculation of local variable changes.
- Tighten up the run view output to allow for wider lines and reduce
  clutter.
- Make the tests pass under python 3.3. Still not doing any live
  testing with python3 apps, but this is a start.
- Add an option to :ref:`command-run` to include modules from the
  standard library. This is disabled by default.
- Add an option to :ref:`command-run` to include modules from the
  ``site-packages`` directory (for third-party installed
  modules). This is enabled by default.
- Add an option to :ref:`command-run` to include a specific package in
  the trace output by name on the command line.
- Updated to Bootstrap 3 CSS framework.
- Add pagination support to the detailed trace report.

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
