def test_basic_usage():
    expect(Number.isInteger(1)).toBe(True)
    expect(Number.isFinite(1.6)).toBe(True)
    expect(typeof(2.2)).toBe('number')

    expect(typeof('str?')).toBe('string')
    expect(typeof(f'a num {1} and a char {"c"}')).toBe('string')

    expect([]).toBeInstanceOf(Array)

    expect({}).toBeInstanceOf(Map)

    expect(tuple()).toBeInstanceOf(Array)
    expect(Object.isFrozen(tuple())).toBe(True)

    expect(set()).toBeInstanceOf(Set)

    def ellipsis():
        ...
    expect(ellipsis()).toBe(undefined)
    expect(typeof(True)).toBe('boolean')
    expect(typeof(False)).toBe('boolean')

    expect(None).toBe(null)


test('basic usage', test_basic_usage)
