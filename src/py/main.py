import ast
import json
import os
from pprint import pprint
import sys

import builders as build
import type_checkers as check
import utils
from utils import consume

import control_flow
import literals


###############################################################################
# MAPPERS

@consume('body')
def map_module(babel_node, node, parents):
    body = babel_node['body']
    docstring = ast.get_docstring(node, clean=True)
    if docstring:
        body = body[1:]
    return {
        'type': 'File',
        'program': {
            'type': 'Program',
            'sourceType': 'module',
            'interpreter': None,
            'body': body,
        },
        'comments': (
            # TODO: use lazy js eval: t.commentBlock(...)
            [{
                'type': 'CommentBlock',
                'value': '/*\n{}\n*/'.format(docstring),
            }]
            if docstring
            else []
        ),
    }


@consume('targets', 'value')
def map_assign(babel_node, node, parents):
    targets = babel_node['targets']
    value = babel_node['value']

    if len(targets) == 1:
        target = targets[0]
        if isinstance(target, ast.Tuple):
            raise ValueError('tuple unpacking is not yet supported')
        elif isinstance(target, ast.List):
            raise ValueError('list unpacking is not yet supported')
        else:
            return {
                'type': 'VariableDeclaration',
                'declarations': [
                    {
                        'type': 'VariableDeclarator',
                        'id': target,
                        'init': value,
                    }
                ],
                'kind': 'var',
            }
    else:
        raise ValueError('assigning to multiple variables is not yet supported')


@consume('targets', 'value')
def map_assign_to_class_prop(babel_node, node, parents):
    targets = babel_node['targets']
    value = babel_node['value']

    if len(targets) == 1:
        target = targets[0]
        # Unpacking is not supported by ES6 => custom implementation
        if isinstance(target, ast.Tuple):
            raise ValueError('tuple unpacking is not yet supported')
        elif isinstance(target, ast.List):
            raise ValueError('list unpacking is not yet supported')
        else:
            return {
                'type': 'ClassProperty',
                # TODO: How to detect this?
                'static': False,
                'computed': False,
                # TODO: ?
                # 'varianace': None,
                'key': target,
                'value': value,
            }
    else:
        raise ValueError('assigning to multiple variables is not yet supported')


@consume('func', 'args', 'keywords')
def map_call(babel_node, node, parents):
    return build.call_expression(
        callee=babel_node['func'],
        args=babel_node['args'],
        keywords=babel_node['keywords'],
    )


@consume('id', 'ctx')
def map_name(babel_node, node, parents):
    # id = node.id
    # one of ast.Load, ast.Store, ast.Delete
    # ctx = node.ctx
    return build.identifier(node.id)


@consume('args', 'body', 'decorator_list', 'returns')
def map_function_def(babel_node, node, parents):
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


def map_lambda(babel_node, node, parents):
    babel_node = dict(babel_node)
    babel_node['body'] = [babel_node['body']]
    return map_function_def(babel_node, node)


@consume('args', 'body', 'decorator_list', 'returns')
def map_function_def_to_class_method(babel_node, node, parents):
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


@consume('bases', 'keywords', 'body', 'decorator_list', 'returns')
def map_class_def(babel_node, node, parents):
    class_name = build.identifier(node.name)
    bases = babel_node['bases']

    if not bases:
        super_class = None
    else:
        if len(bases) == 1:
            super_class = bases[0]
        else:
            super_class = build.call_expression(
                # TODO: Use constant
                callee=build.identifier('__multi__'),
                args=bases,
                ensure_native_compatibility=False,
            )

    body = babel_node['body']

    # Change functions to methods and variable declarations to class properties
    # that were created by the recursion already.

    class_expression = {
        'type': 'ClassExpression',
        'id': class_name,
        'superClass': super_class,
        'body': {
            'type': 'ClassBody',
            'body': body,
        },
    }

    if babel_node['keywords']:
        print('keywords was provided for class definition. ignored...')

    return {
        'type': 'VariableDeclaration',
        'declarations': [
            {
                'type': 'VariableDeclarator',
                'id': class_name,
                'init': utils.apply_decorators(
                    babel_node['decorator_list'],
                    build.call_expression(
                        # TODO: Use constant
                        callee=build.identifier('__def__'),
                        args=[class_expression],
                        ensure_native_compatibility=False,
                    )
                ),
            }
        ],
        'kind': 'var',
    }


###############################################################################
def func_name_to_node_name(func_name):
    snake_node_name = func_name.replace('map_', '', 1)
    return ''.join(
        word.capitalize()
        for word in snake_node_name.split('_')
    )


def get_mappers(module):
    module_dict = module.__dict__
    return {
        func_name_to_node_name(name): module_dict[name]
        for name in module_dict
        if name.startswith('map_')
    }


mapping = {
    **get_mappers(literals),
    **get_mappers(control_flow),

    'Module': map_module,
    'Expr': lambda babel_node, node, parents: {
        'type': 'ExpressionStatement',
        'expression': babel_node['value'],
    },
    'Pass': lambda babel_node, node, parents: {
        'type': 'EmptyStatement',
    },
    'Assign': lambda babel_node, node, parents: (
        map_assign_to_class_prop(babel_node, node, parents)
        if parents and isinstance(parents[0], ast.ClassDef)
        else map_assign(babel_node, node, parents)
    ),
    'Call': map_call,
    'Name': map_name,
    'Store': lambda babel_node, node, parents: {},

    'ClassDef': map_class_def,

    'FunctionDef': lambda babel_node, node, parents: (
        map_function_def_to_class_method(babel_node, node, parents)
        if parents and isinstance(parents[0], ast.ClassDef)
        else map_function_def(babel_node, node, parents)
    ),
    'Lambda': map_lambda,
    'Arguments': lambda babel_node, node, parents: babel_node,
    'Arg': lambda babel_node, node, parents: build.identifier(node.arg),
    'Starred': lambda babel_node, node, parents: {
        **babel_node['value'],
        'starred': True,
    },
    'Keyword': lambda babel_node, node, parents: {
        'arg': None if node.arg is None else build.identifier(node.arg),
        'value': babel_node['value'],
    },
}


def complete_babel_node(incomplete_babel_node_with_children, node, parents):
    if node.__class__.__name__ in mapping:
        print('yes', node.__class__.__name__)
        # print(incomplete_babel_node_with_children)
        node_name = node.__class__.__name__
        key = node_name[0].upper() + node_name[1:]
        map_node = mapping[key]
        completion = map_node(incomplete_babel_node_with_children, node, parents)
        incomplete_babel_node_with_children.update(completion)
        pprint(incomplete_babel_node_with_children)
    else:
        print('oops', node.__class__.__name__)


def create_babel_node(node, parents=tuple()):
    if node is None:
        return None

    if not isinstance(node, ast.AST):
        print('uoh', node)
    babel_node = {
        'type': None,
        # 'loc': {
        #     'start': {
        #         'line': getattr(node, 'lineno', 0) - 1,
        #         'column': getattr(node, 'col_offset', 0) - 1,
        #     },
        #     'end': {
        #         'line': -1,
        #         'column': -1,
        #     },
        # },
    }
    # The root node is last.
    parents_with_current = (node,) + parents
    for field, value in ast.iter_fields(node):
        if isinstance(value, list):
            babel_node[field] = [
                create_babel_node(item, parents_with_current)
                for item in value
                # if isinstance(item, ast.AST)
            ]
        elif isinstance(value, ast.AST):
            babel_node[field] = create_babel_node(value, parents_with_current)
    complete_babel_node(babel_node, node, parents)
    return babel_node


###############################################################################
if sys.version_info < (3, 5, 0):
    raise EnvironmentError('You need at least python 3.5.0')

# print('argv', sys.argv)

base_dir = os.path.dirname(os.path.abspath(__file__))
source_filename = os.path.join(base_dir, 'test.py')
json_dump_filename = os.path.join(base_dir, 'test.json')

try:
    with open(source_filename) as file:
        code = file.read()
        abstract_syntax_tree = ast.parse(code, source_filename)
        # visitor = Visitor()
        # print(visitor.visit(ast))
        babel_ast = create_babel_node(abstract_syntax_tree)
        ast_json = json.dumps(babel_ast)
        # print(ast_json)
        with open(json_dump_filename, 'w') as json_file:
            json_file.write(ast_json)
        # print()
        print(json_dump_filename)
        # print(ast_json)
        sys.exit(0)
except Exception as e:
    raise e
    # print(str(e))
    sys.exit(1)
