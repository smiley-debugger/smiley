import sys

import test_funcs

if __name__ == '__main__':
    print 'Running', __file__
    test_funcs.a()
    if '-e' in sys.argv:
        raise RuntimeError('test exception')
