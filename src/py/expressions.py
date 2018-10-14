import builders as build
from utils import consume


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
