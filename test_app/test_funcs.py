
def gen(m):
    for i in xrange(m):
        yield i


def c(input):
    print 'input =', input
    data = list(gen(input))
    print 'Leaving c()'


def b(arg):
    val = arg * 5
    c(val)
    print 'Leaving b()'
    return val


def a():
    print 'args:', sys.argv
    b(2)
    print 'Leaving a()'
