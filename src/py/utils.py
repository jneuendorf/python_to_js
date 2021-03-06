# import itertools
import functools

# import type_checkers as check
import builders as build
from js_helper_names import JsHelperNames


def consume(*props):
    '''Decorator for removing auto-copied props from the babel nodes:
    The mapping consumes props from an AST node especially when renaming
    props.'''
    def decorator(map_node):
        def wrapper(babel_node, node, parents):
            result = map_node(babel_node, node, parents)
            for prop in props:
                if prop in babel_node:
                    del babel_node[prop]
                # else:
                #     print('INFO: consuming not existing prop', prop)
            return result
        return wrapper
    return decorator


# def groupby(iterable, key=lambda x: x):
#     return itertools.groupby(
#         sorted(iterable, key=key),
#         key=key,
#     )


def reduce(operator, nodes):
    '''
    Creates an ast containing binary nodes from a (flat) list of items.

    Example:
    sum = reduce(
        operator=lambda left, right: build.binary_expression('+', left, right),
        nodes=[build.num(i) for i in range(0, 10)]
    )
    '''
    if len(nodes) < 2:
        raise ValueError('There must be at least 2 nodes.')
    # reduced_node = operator()
    return functools.reduce(operator, nodes)


def binary_expression(raw_operator, nodes):
    def reducer(left, right):
        return build.binary_expression(raw_operator, left, right)
    return reduce(reducer, nodes)


###############################################################################

concatenation = functools.partial(binary_expression, '+')
sum = concatenation


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
                # TODO: Support third-party/built-in decorators? If so set this to 'True'
                ensure_native_compatibility=False,
            )
    return decorated_node


class ShapeError(ValueError):
    pass


def unpack_value(node, shape_descriptor):
    '''Retrives a value from a babel node.

    'shape_descriptor' is a string. There are 2 kinds of delimiters:
    dots and '__'. Dots separate node types and optionally '__' separates
    the type from the key name of the next nested node. If no '__' is
    provided the nested node is expected in the non-'type' property.

    Example:


    The 'node' {
        'type': 'PARENT',
        'child': {
            'type': 'CHILD',
            'a': [...],
            'b': {
                'type': 'B'
                'answer': 42,
            }
        }
    }
    and the 'shape_descriptor' 'PARENT.CHILD__b.B__answer' results in '42'.
    '''
    current_node = node
    parts = shape_descriptor.split('.')
    last_index = len(parts) - 1
    for i, part in enumerate(parts):
        if '__' in part:
            node_type, child_key = part.split('__')
            child_key_explicit = True
        else:
            node_type = part
            child_key = [k for k in current_node.keys() if k != 'type'][0]
            child_key_explicit = False

        # snake_case to PascalCase.
        node_type = ''.join(word.capitalize() for word in node_type.split('_'))

        if current_node['type'] != node_type:
            print(node)
            raise ShapeError(
                'Invalid node type \'{}\'. Expected \'{}\''
                .format(current_node['type'], node_type)
            )

        # Omitting the key for the last part is ok because we don't
        # need/want to look further.
        if i < last_index:
            if not child_key_explicit and len(current_node.keys()) != 2:
                raise ShapeError(
                    '\'{}\' has 1 or more than 2 keys but no key name was provided.'
                    .format(node_type)
                )
            current_node = current_node[child_key]
        else:
            return current_node[child_key]


def shape(node, shape_descriptor):
    last_node_type = shape_descriptor.split('.')[-1]
    if '__' in last_node_type:
        raise ShapeError(
            'Last part must not contain a key but only the node type.'
        )
    try:
        return (
            unpack_value(node, shape_descriptor + '__type')
            == last_node_type
        )
    except ShapeError as e:
        print(str(e))
        return False


def get_callee_name(node, raw=False):
    shape_descriptor = (
        'expression.condition_expression__alternate'
        '.call_expression__callee'
    )
    if raw:
        shape_descriptor += '.identifier__name'
    return unpack_value(node, shape_descriptor)


# Used for id equality check.
NO_DEFAULT_FOR_ARG = tuple()


def function_definition_parts(babel_node, node):
    '''Returns parts of the function babel AST node that are common for normal
    function definitions and class/instance methods.'''

    arguments = babel_node['args']
    args = arguments.get('args', [])
    defaults = arguments.get('defaults', [])
    vararg = arguments.get('vararg', None)
    kwonlyargs = arguments.get('kwonlyargs', [])
    kw_defaults = arguments.get('kw_defaults', [])
    kwarg = arguments.get('kwarg', None)

    diff = len(args) - len(defaults)
    if diff > 0:
        defaults = [NO_DEFAULT_FOR_ARG for i in range(0, diff)] + defaults

    # Prepend custom JS code the function body (for creating the kwargs behavior).
    # body = babel_node['body']
    # if len(args) > 0:
    args_identifier = '__arguments__'
    if True:
        # var [[a, b=1, ...c], {d, e=3, ...f}] =  __get_args__(args)
        body = (
            [
                build.variable_declaration(
                    left=build.array_destructuring(
                        bare_pattern=True,
                        props=[
                            build.array_destructuring(
                                props=[
                                    (
                                        arg
                                        if defaults[i] is NO_DEFAULT_FOR_ARG
                                        else (arg, defaults[i])
                                    )
                                    for i, arg in enumerate(args)
                                ],
                                rest=vararg,
                                bare_pattern=True,
                            ),
                            build.object_destructuring(
                                props=[
                                    (
                                        kwonlyarg
                                        if kw_defaults[i] is None
                                        else (kwonlyarg, kw_defaults[i])
                                    )
                                    for i, kwonlyarg in enumerate(kwonlyargs)
                                ],
                                rest=kwarg,
                                bare_pattern=True,
                            ),
                        ]
                    ),
                    right=build.call_expression(
                        callee=build.identifier(JsHelperNames.GET_ARGS_AND_KWARGS),
                        args=[build.identifier(args_identifier)],
                        ensure_native_compatibility=False,

                    ),
                ),
            ]
            + [
                build.assignment(
                    left=arg,
                    right=build.call_expression(
                        callee=build.identifier(
                            JsHelperNames.CONSUME_KWARG_IF_POSSIBLE
                        ),
                        args=[
                            kwarg,
                            arg,
                            build.string(arg['name'])
                        ],
                        ensure_native_compatibility=False,
                    ),
                )
                for arg in args
                if kwarg is not None
            ]
            + babel_node['body']
        )

    return {
        '__name__': build.identifier(node.name),
        'params': [
            build.rest(build.identifier(args_identifier))
            # build.array_destructuring(
            #     props=[
            #         (
            #             arg
            #             if defaults[i] is NO_DEFAULT_FOR_ARG
            #             else (arg, defaults[i])
            #         )
            #         for i, arg in enumerate(args)
            #     ],
            #     rest=vararg,
            #     bare_pattern=True,
            # ),
            # build.object_destructuring(
            #     props=[
            #         (
            #             kwonlyarg
            #             if kw_defaults[i] is None
            #             else (kwonlyarg, kw_defaults[i])
            #         )
            #         for i, kwonlyarg in enumerate(kwonlyargs)
            #     ],
            #     rest=kwarg,
            #     bare_pattern=True,
            # ),
        ],
        'body': {
            'type': 'BlockStatement',
            'body': body,
            'directives': [],
        },
    }
