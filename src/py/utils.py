import itertools


def groupby(iterable, key=lambda x: x):
    return itertools.groupby(
        sorted(iterable, key=key),
        key=key,
    )
