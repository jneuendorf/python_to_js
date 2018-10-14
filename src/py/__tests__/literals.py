# def ff(a, b=1, *c, d, e=3, **f):
#     pass


def test_basic_usage():
    expect([]).toBeInstanceOf(Array)


test('basic usage', test_basic_usage)
