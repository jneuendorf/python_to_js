import ast

import builders as build
from utils import consume, JsHelperNames


def map_num(babel_node, node, parents):
    return {
        'type': 'NumericLiteral',
        'value': node.n,
    }


def map_str(babel_node, node, parents):
    return {
        'type': 'StringLiteral',
        'value': node.s,
    }


@consume('value')
def map_name_constant(babel_node, node, parents):
    if type(node.value) is bool:
        return {'type': 'BooleanLiteral', 'value': node.value}
    else:
        return {'type': 'NullLiteral'}


@consume('elts', 'ctx')
def map_list(babel_node, node, parents):
    print('>>', babel_node, node.ctx)
    if isinstance(node.ctx, ast.Load):
        return build.array_expression(babel_node['elts'])
    else:
        raise ValueError('TODO array destructuring')


def map_tuple(babel_node, node, parents):
    mapped_list = map_list(babel_node, node, parents)
    if isinstance(node.ctx, ast.Load):
        return build.call_expression(
            callee=build.identifier(JsHelperNames.TUPLE_CONSTRUCTOR),
            args=[mapped_list],
            ensure_native_compatibility=False,
        )
    else:
        return mapped_list


@consume('elts')
def map_set(babel_node, node, parents):
    return {
        'type': 'NewExpression',
        'callee': build.identifier('Set'),
        'arguments': babel_node['elts'],
    }


@consume('keys', 'values')
def map_dict(babel_node, node, parents):
    return build.call_expression(
        callee=build.identifier(JsHelperNames.DICT_CONSTRUCTOR),
        args=[build.array_expression([
            (
                build.array_expression([key, value])
                if key is not None
                else build.spread(
                    build.call_expression(
                        callee=build.member_expression(
                            object=value,
                            property=build.identifier('entries'),
                        ),
                        ensure_native_compatibility=False,
                    )
                )
            )
            for key, value in zip(babel_node['keys'], babel_node['values'])
        ])],
    )
    # return {
    #     'type': 'ObjectExpression',
    #     'properties': [
    #         build.spread(value) if key is None else build.object_property(key, value)
    #         for key, value in zip(babel_node['keys'], babel_node['values'])
    #     ],
    # }
