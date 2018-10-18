def test_basic_usage():
    expect(Number.isInteger(1)).toBe(True)
    expect(Number.isFinite(1.6)).toBe(True)
    expect(typeof(2.2)).toBe('number')

    expect(typeof('str?')).toBe('string')
    expect(typeof(f'a num {1} and a char {"c"}')).toBe('string')

    expect([]).toBeInstanceOf(Array)

    expect({}).toBeInstanceOf(dict)

    expect(tuple()).toBeInstanceOf(Array)
    expect(Object.isFrozen(tuple())).toBe(True)

    expect(set()).toBeInstanceOf(Set)

    def ellipsis():
        ...
    expect(ellipsis()).toBe(undefined)
    expect(typeof(True)).toBe('boolean')
    expect(typeof(False)).toBe('boolean')

    expect(None).toBe(null)


def test_dict():
    non_string_key = ['array']
    d = dict(
        [['a', 1], ['b', 2], [non_string_key, 'non_string_key']],
        c=3,
        # overwrite 'b' from iterable argument
        b=4,
    )

    expect(len(d)).toBe(4)

    expect(d.get('a')).toBe(1)
    expect(d['a']).toBe(1)

    expect(d['b']).toBe(4)
    expect(d['c']).toBe(3)
    expect(d[non_string_key]).toBe('non_string_key')
    # console.log([1,2,3][1:3])


test('basic usage', test_basic_usage)
test('dict', test_dict)
