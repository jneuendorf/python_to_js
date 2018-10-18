import ast

import builders as build
from utils import consume
from js_helper_names import JsHelperNames


@consume('value')
def map_expr(babel_node, node, parents):
    return build.expression_statement(babel_node['value'])


@consume('func', 'args', 'keywords')
def map_call(babel_node, node, parents):
    return build.call_expression(
        callee=babel_node['func'],
        args=babel_node['args'],
        keywords=babel_node['keywords'],
    )


def map_keyword(babel_node, node, parents):
    return {
        'arg': None if node.arg is None else build.identifier(node.arg),
        'value': babel_node['value'],
    }


@consume('value', 'attr', 'ctx')
def map_attribute(babel_node, node, parents):
    return build.member_expression(
        object=babel_node['value'],
        property=build.identifier(node.attr),
    )


# Subscripting
@consume('value', 'slice', 'ctx')
def map_subscript(babel_node, node, parents):
    if isinstance(node.slice, ast.ExtSlice):
        raise ValueError('Advanced slicing (ExtSlice) is not supported.')

    args = [babel_node['value']]
    slice_data = babel_node['slice']
    if isinstance(node.slice, ast.Index):
        args += [
            build.string('index'),
            slice_data['value'],
        ]
    # isinstance(node.slice, ast.Slice)
    else:
        args += [
            build.string('slice'),
            slice_data['lower'],
            slice_data['upper'],
            slice_data['step'],
        ]

    return build.call_expression(
        callee=build.identifier(JsHelperNames.SUBSCRIPT),
        args=args,
        ensure_native_compatibility=False,
    )


def map_index(babel_node, node, parents):
    return babel_node


def map_slice(babel_node, node, parents):
    # if e.g. 'node.lower is None' it is not contained in 'babel_node'.
    # Thus we must make sure the keys exist in any case.
    return {
        'lower': build.undefined(),
        'upper': build.undefined(),
        'step': build.undefined(),
        **babel_node,
    }
