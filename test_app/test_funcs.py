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


def large_data_structure():
    big_data = {
        'key': {
            'nested_key': 'nested_value',
            'further': {
                'deeper': [
                    'lots of values',
                    'in this list',
                ],
            },
        },
    }
    big_data['key2'] = 'key'


def a():
    print('args:', sys.argv)
    b(2)
    produce_error()
    large_data_structure()
    print('Leaving a()')
