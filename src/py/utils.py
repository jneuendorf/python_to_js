import itertools

# import type_checkers as check


def groupby(iterable, key=lambda x: x):
    return itertools.groupby(
        sorted(iterable, key=key),
        key=key,
    )


def unwrap_ensured_native_compatibility_call(babel_node):
    if 'expression' in babel_node and 'alternate' in babel_node['expression']:
        return babel_node['expression']['alternate']
    # It's not a wrapped call expression => return the node
    return babel_node
