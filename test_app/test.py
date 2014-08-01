import sys
import threading

import test_funcs

if __name__ == '__main__':
    print 'Running', __file__
    if '-t' in sys.argv:
        print 'Starting a thread'
        t = threading.Thread(target=test_funcs.a)
        t.start()
        t.join()
    else:
        test_funcs.a()
    if '-e' in sys.argv:
        raise RuntimeError('test exception')
