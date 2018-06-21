from __future__ import print_function

import sys
import threading

import test_funcs

if __name__ == '__main__':
    print('Running', __file__)
    if '-t' in sys.argv:
        threads = []
        for i in range(3):
            t = threading.Thread(target=test_funcs.a)
            print('Starting thread', t.name)
            t.start()
            threads.append(t)
        for t in threads:
            print('Waiting for', t.name)
            t.join()
    elif '-m' in sys.argv:
        test_funcs.run_many_functions(10, 4)
    else:
        test_funcs.a()
    if '-e' in sys.argv:
        raise RuntimeError('test exception')
