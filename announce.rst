===========================================
 Smiley 0.6.0 -- Python Application Tracer
===========================================

.. tags:: smiley release python

What is smiley?
===============

*Smiley spies on your Python app while it runs.*

Smiley_ includes several subcommands for running Python programs and
monitoring all of the internal details for recording and
reporting. For more details, see the documentation_.

What's New?
===========

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
- Add an option to ``run`` to include modules from the
  standard library. This is disabled by default.
- Add an option to ``run`` to include modules from the
  ``site-packages`` directory (for third-party installed
  modules). This is enabled by default.
- Add an option to ``run`` to include a specific package in
  the trace output by name on the command line.
- Updated to Bootstrap 3 CSS framework.
- Add pagination support to the detailed trace report.

.. _smiley: https://github.com/dhellmann/smiley

.. _documentation: https://smiley.readthedocs.org/en/latest/

