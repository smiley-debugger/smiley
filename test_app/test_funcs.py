from __future__ import print_function

import sys


def gen(m):
    for i in xrange(m):
        yield i


def c(input):
    print('input =', input)
    data = list(gen(input))
    print('Leaving c()', data)


def b(arg):
    val = arg * 5
    c(val)
    print('Leaving b()')
    return val


def produce_error():
    try:
        b('invalid')
    except Exception as err:
        print('Error:', err)


def a():
    print('args:', sys.argv)
    b(2)
    produce_error()
    print('Leaving a()')
