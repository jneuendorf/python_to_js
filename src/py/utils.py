import itertools

# import type_checkers as check
import builders as build


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


def apply_decorators(decorator_list, undecorated_node):
    decorated_node = undecorated_node
    if decorator_list:
        for decorator in reversed(decorator_list):
            dec = unwrap_ensured_native_compatibility_call(decorator)
            decorated_node = build.call_expression(
                callee=dec,
                args=[decorated_node],
                ensure_native_compatibility=False,
            )
    return decorated_node
