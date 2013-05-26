=============
 Quick Start
=============

Installing
==========

Install with ``pip``::

  $ pip install smiley

Using
=====

*This quick-start is not a complete reference for the command line
program and its options. Use the help subcommand for more
details.*

In one terminal window, run the ``monitor`` command::

  $ smiley monitor

In a second terminal window, use smiley to run an application. This
example uses ``test.py`` from the ``test_app`` directory in the smiley
source tree.

::

  $ smiley run ./test.py
  args: ['./test.py']
  input = 10
  Leaving c() [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
  Leaving b()
  Leaving a()

The monitor session will show the execution path and local variables
for the app.

::
    
    Starting new run: ./test.py
    test.py:   1: import test_funcs
    test.py:   1: import test_funcs
    test_funcs.py:   1: import sys
    test_funcs.py:   1: import sys
    test_funcs.py:   3: def gen(m):
    test_funcs.py:   8: def c(input):
    test_funcs.py:  14: def b(arg):
    test_funcs.py:  21: def a():
    test_funcs.py:  21: return>>> None
    test.py:   3: if __name__ == '__main__':
    test.py:   4:     test_funcs.a()
    test_funcs.py:  21: def a():
    test_funcs.py:  22:     print 'args:', sys.argv
    test_funcs.py:  23:     b(2)
    test_funcs.py:  14: def b(arg):
                        arg = 2
    test_funcs.py:  15:     val = arg * 5
                        arg = 2
    test_funcs.py:  16:     c(val)
                        arg = 2
                        val = 10
    test_funcs.py:   8: def c(input):
                        input = 10
    test_funcs.py:   9:     print 'input =', input
                        input = 10
    test_funcs.py:  10:     data = list(gen(input))
                        input = 10
    test_funcs.py:   3: def gen(m):
                        m = 10
    test_funcs.py:   4:     for i in xrange(m):
                        m = 10
    test_funcs.py:   5:         yield i
                        i = 0
                        m = 10
    test_funcs.py:   5: return>>> 0
    test_funcs.py:   5:         yield i
                        i = 0
                        m = 10
    test_funcs.py:   4:     for i in xrange(m):
                        i = 0
                        m = 10
    test_funcs.py:   5:         yield i
                        i = 1
                        m = 10
    test_funcs.py:   5: return>>> 1
    test_funcs.py:   5:         yield i
                        i = 1
                        m = 10
    test_funcs.py:   4:     for i in xrange(m):
                        i = 1
                        m = 10
    test_funcs.py:   5:         yield i
                        i = 2
                        m = 10
    test_funcs.py:   5: return>>> 2
    test_funcs.py:   5:         yield i
                        i = 2
                        m = 10
    test_funcs.py:   4:     for i in xrange(m):
                        i = 2
                        m = 10
    test_funcs.py:   5:         yield i
                        i = 3
                        m = 10
    test_funcs.py:   5: return>>> 3
    test_funcs.py:   5:         yield i
                        i = 3
                        m = 10
    test_funcs.py:   4:     for i in xrange(m):
                        i = 3
                        m = 10
    test_funcs.py:   5:         yield i
                        i = 4
                        m = 10
    test_funcs.py:   5: return>>> 4
    test_funcs.py:   5:         yield i
                        i = 4
                        m = 10
    test_funcs.py:   4:     for i in xrange(m):
                        i = 4
                        m = 10
    test_funcs.py:   5:         yield i
                        i = 5
                        m = 10
    test_funcs.py:   5: return>>> 5
    test_funcs.py:   5:         yield i
                        i = 5
                        m = 10
    test_funcs.py:   4:     for i in xrange(m):
                        i = 5
                        m = 10
    test_funcs.py:   5:         yield i
                        i = 6
                        m = 10
    test_funcs.py:   5: return>>> 6
    test_funcs.py:   5:         yield i
                        i = 6
                        m = 10
    test_funcs.py:   4:     for i in xrange(m):
                        i = 6
                        m = 10
    test_funcs.py:   5:         yield i
                        i = 7
                        m = 10
    test_funcs.py:   5: return>>> 7
    test_funcs.py:   5:         yield i
                        i = 7
                        m = 10
    test_funcs.py:   4:     for i in xrange(m):
                        i = 7
                        m = 10
    test_funcs.py:   5:         yield i
                        i = 8
                        m = 10
    test_funcs.py:   5: return>>> 8
    test_funcs.py:   5:         yield i
                        i = 8
                        m = 10
    test_funcs.py:   4:     for i in xrange(m):
                        i = 8
                        m = 10
    test_funcs.py:   5:         yield i
                        i = 9
                        m = 10
    test_funcs.py:   5: return>>> 9
    test_funcs.py:   5:         yield i
                        i = 9
                        m = 10
    test_funcs.py:   4:     for i in xrange(m):
                        i = 9
                        m = 10
    test_funcs.py:   4: return>>> None
    test_funcs.py:  11:     print 'Leaving c()', data
                        data = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                        input = 10
    test_funcs.py:  11: return>>> None
    test_funcs.py:  17:     print 'Leaving b()'
                        arg = 2
                        val = 10
    test_funcs.py:  18:     return val
                        arg = 2
                        val = 10
    test_funcs.py:  18: return>>> 10
    test_funcs.py:  24:     print 'Leaving a()'
    test_funcs.py:  24: return>>> None
    test.py:   4: return>>> None
    Finished run
