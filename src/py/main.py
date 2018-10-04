import ast
from collections import namedtuple
import json
import os
from pprint import pprint
import sys

import builders as build
import type_checkers as check


JsHelperNames = namedtuple('JsHelperNames', ' '.join([
    # keys
    'CONSUME_KWARG_IF_POSSIBLE',
]))(
    # values
    '__use_kwarg__',
)


def consume(*props):
    '''Decorator for removing auto-copied props from the babel nodes:
    The mapping consumes props from an AST node especially when renaming
    props.'''
    def decorator(map_node):
        def wrapper(babel_node, node):
            result = map_node(babel_node, node)
            for prop in props:
                if prop in babel_node:
                    del babel_node[prop]
                # else:
                #     print('INFO: consuming not existing prop', prop)
            return result
        return wrapper
    return decorator


###############################################################################
# MAPPERS

@consume('body')
def map_module(babel_node, node):
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
def map_assign(babel_node, node):
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
                'type': 'AssignmentExpression',
                'operator': '=',
                'left': target,
                'right': value,
            }
    else:
        raise ValueError('assigning to multiple variables is not yet supported')


@consume('func', 'args', 'keywords')
def map_call(babel_node, node):
    # print('>>>>>>>>')
    # pprint([keyword['arg'] for keyword in babel_node['keywords']])
    return build.call_expression(
        callee=babel_node['func'],
        args=babel_node['args'],
        keywords=babel_node['keywords'],
    )
    # return {
    #     'type': 'CallExpression',
    #     'callee': babel_node['func'],
    #     'arguments': [
    #         {
    #             'type': 'ArrayExpression',
    #             'elements': [
    #                 (
    #                     {'type': 'SpreadElement', 'argument': arg}
    #                     if 'starred' in arg and arg['starred'] is True
    #                     else arg
    #                 )
    #                 for arg in babel_node['args']
    #             ],
    #         },
    #         {
    #             'type': 'ObjectExpression',
    #             'properties': [
    #                 (
    #                     {'type': 'SpreadElement', 'argument': keyword['value']}
    #                     if keyword['arg'] is None
    #                     else build.object_property(
    #                         key=keyword['arg'],
    #                         value=keyword['value'],
    #                     )
    #                 )
    #                 for keyword in babel_node['keywords']
    #             ],
    #         },
    #     ],
    # }


@consume('id', 'ctx')
def map_name(babel_node, node):
    # id = node.id
    # one of ast.Load, ast.Store, ast.Delete
    # ctx = node.ctx
    return build.identifier(node.id)


@consume('args', 'body', 'decorator_list', 'returns')
def map_function_def(babel_node, node):
    arguments = babel_node['args']
    args = arguments.get('args', [])
    defaults = arguments.get('defaults', [])
    vararg = arguments.get('vararg', None)
    kwonlyargs = arguments.get('kwonlyargs', [])
    kw_defaults = arguments.get('kw_defaults', [])
    kwarg = arguments.get('kwarg', None)

    NO_DEFAULT = []
    diff = len(args) - len(defaults)
    if diff > 0:
        defaults = [NO_DEFAULT for i in range(0, diff)] + defaults

    # TODO: decorators
    decorator_list = babel_node['decorator_list']
    print('>>')
    pprint(decorator_list)
    # if check.is_identifier(decorator)
    # for decorator in decorator_list
    # print(list(enumerate(kwonlyargs)), kw_defaults)
    body = (
        [
            build.assignment(
                left=arg,
                right=build.call_expression(
                    callee=build.identifier(JsHelperNames.CONSUME_KWARG_IF_POSSIBLE),
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
    func_name = build.identifier(node.name)
    res = {
        'type': 'FunctionDeclaration',
        'id': func_name,
        'params': [
            build.array_destructuring(
                props=[
                    (
                        arg
                        if defaults[i] is NO_DEFAULT
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
        ],
        'body': {
            'type': 'BlockStatement',
            'body': body,
            'directives': [],
        },
    }
    # return res
    return {
        'type': 'VariableDeclaration',
        'declarations': [
            {
                'type': 'VariableDeclarator',
                'id': func_name,
                'init': build.call_expression(
                    # TODO: Use constant
                    callee=build.identifier('__def__'),
                    args=[res],
                    ensure_native_compatibility=False,
                ),
            }
        ],
        'kind': 'var',
    }


def map_lambda(babel_node, node):
    babel_node = dict(babel_node)
    babel_node['body'] = [babel_node['body']]
    return map_function_def(babel_node, node)


###############################################################################
mapping = {
    'Module': map_module,
    'Expr': lambda babel_node, node: {
        'type': 'ExpressionStatement',
        'expression': babel_node['value'],
    },
    'Pass': lambda babel_node, node: {
        'type': 'EmptyStatement',
    },
    'Assign': map_assign,
    'Call': map_call,
    'Name': map_name,
    'Num': lambda babel_node, node: {
        'type': 'NumericLiteral',
        'value': node.n,
    },
    'Str': lambda babel_node, node: {
        'type': 'StringLiteral',
        'value': node.s,
    },
    'Store': lambda babel_node, node: {},

    'FunctionDef': map_function_def,
    'Lambda': map_lambda,
    'arguments': lambda babel_node, node: babel_node,
    'arg': lambda babel_node, node: build.identifier(node.arg),
    'Starred': lambda babel_node, node: {
        **babel_node['value'],
        'starred': True,
    },
    'keyword': lambda babel_node, node: {
        'arg': None if node.arg is None else build.identifier(node.arg),
        'value': babel_node['value'],
    },
}


def complete_babel_node(incomplete_babel_node_with_children, node):
    if node.__class__.__name__ in mapping:
        print('yes', node.__class__.__name__)
        # print(incomplete_babel_node_with_children)
        map_node = mapping[node.__class__.__name__]
        completion = map_node(incomplete_babel_node_with_children, node)
        incomplete_babel_node_with_children.update(completion)
        pprint(incomplete_babel_node_with_children)
    else:
        print('oops', node.__class__.__name__)


def create_babel_node(node):
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
    for field, value in ast.iter_fields(node):
        if isinstance(value, list):
            babel_node[field] = [
                create_babel_node(item)
                for item in value
                # if isinstance(item, ast.AST)
            ]
        elif isinstance(value, ast.AST):
            babel_node[field] = create_babel_node(value)
    complete_babel_node(babel_node, node)
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
