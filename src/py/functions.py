import ast

import builders as build
import utils
from utils import consume


@consume('args', 'body', 'decorator_list', 'returns')
def _map_function_def(babel_node, node, parents):
    common_parts = utils.function_definition_parts(babel_node, node)
    func_name = common_parts['__name__']
    params = common_parts['params']
    body = common_parts['body']

    function_definition = build.call_expression(
        # TODO: Use constant
        callee=build.identifier('__def__'),
        args=[{
            'type': 'FunctionExpression',
            'id': func_name,
            'params': params,
            'body': body,
        }],
        ensure_native_compatibility=False,
    )
    return {
        'type': 'VariableDeclaration',
        'declarations': [
            {
                'type': 'VariableDeclarator',
                'id': func_name,
                'init': utils.apply_decorators(
                    babel_node['decorator_list'],
                    function_definition
                ),
            }
        ],
        'kind': 'var',
    }


@consume('args', 'body', 'decorator_list', 'returns')
def _map_function_def_to_class_method(babel_node, node, parents):
    common_parts = utils.function_definition_parts(babel_node, node)
    method_name = common_parts['__name__']
    raw_method_name = method_name['name']
    params = common_parts['params']
    body = common_parts['body']

    decorators = []

    use_static_keyword = False
    inject_self = True
    for decorator in babel_node['decorator_list']:
        # '@classmethod' does not take any arguments
        # => it must be an identifier.
        decorator_is_identifier = check.is_identifier(decorator)
        decorator_requires_static_keyword = (
            decorator_is_identifier
            and decorator['name'] in ['classmethod', 'staticmethod']
        )
        if decorator_requires_static_keyword:
            use_static_keyword = True
            if decorator['name'] == 'staticmethod':
                inject_self = False
        else:
            if decorator_is_identifier:
                expression = decorator
            else:
                # Use the kwargs supporting way to call the function to avoid
                # actual expression as decorator which is technically possible.
                # NOTE: This corresponds to
                # 'build.call_expression(ensure_native_compatibility=False)'
                # in 'utils.apply_decorators'.
                expression = utils.unpack_value(
                    decorator,
                    'expression_statement.conditional_expression__consequent'
                )
            decorators.append({'type': 'Decorator', 'expression': expression})

    # Remove 'self' as 1st positional argument
    # and remove 'self = __use_kwarg__(_, self, "self");'
    # and instead inject 'var self = this' into the method body.
    del params[0]['elements'][0]
    inner_body = body['body']
    if inner_body:
        del inner_body[0]
    if inject_self:
        inner_body.insert(0, build.variable_declaration(
            left=build.identifier('self'),
            right=build.this(),
        ))

    return {
        'type': 'ClassMethod',
        'kind': (
            'constructor'
            if raw_method_name == 'constructor'
            else 'method'
        ),
        'decorators': decorators,
        'static': use_static_keyword,
        'key': method_name,
        'params': params,
        'body': body,
        'id': None,
        'generator': False,
        'expression': False,
        'async': False,
    }


def map_function_def(babel_node, node, parents):
    if parents and isinstance(parents[0], ast.ClassDef):
        return _map_function_def_to_class_method(babel_node, node, parents)
    else:
        return _map_function_def(babel_node, node, parents)


def map_lambda(babel_node, node, parents):
    babel_node = dict(babel_node)
    babel_node['body'] = [babel_node['body']]
    return map_function_def(babel_node, node)


# @consume('args', 'vararg', 'kwonlyargs', 'kwarg', 'defaults', 'kw_defaults')
def map_arguments(babel_node, node, parents):
    return babel_node


@consume('arg', 'annotation')
def map_arg(babel_node, node, parents):
    return build.identifier(node.arg)


@consume('value')
def map_starred(babel_node, node, parents):
    return {
        **babel_node['value'],
        'starred': True,
    }
