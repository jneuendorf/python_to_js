import ast
import json
import os
from pprint import pprint
import sys

import builders as build
import type_checkers as check
import utils
from utils import consume

import classes
import control_flow
import expressions
import functions
import literals
import statements
import variables


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
    **get_mappers(classes),
    **get_mappers(control_flow),
    **get_mappers(expressions),
    **get_mappers(functions),
    **get_mappers(literals),
    **get_mappers(statements),
    **get_mappers(variables),

    'Module': map_module,
    'Pass': lambda babel_node, node, parents: {
        'type': 'EmptyStatement',
    },
    'Store': lambda babel_node, node, parents: {},
}

# print(list(mapping.keys()))


def complete_babel_node(incomplete_babel_node_with_children, node, parents):
    node_name = node.__class__.__name__
    key = node_name[0].upper() + node_name[1:]
    if key in mapping:
        print('yes', node.__class__.__name__)
        # print(incomplete_babel_node_with_children)
        # print('===============================')
        # print(node_name, key)
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
min_version = (3, 5, 0)
if sys.version_info < min_version:
    raise EnvironmentError(
        'You need at least python {}'
        .format('.'.join(min_version))
    )

# print('argv', sys.argv)

base_dir = os.path.dirname(os.path.abspath(__file__))
# source_filename = os.path.join(base_dir, 'test.py')
# json_dump_filename = os.path.join(base_dir, 'test.json')

try:
    source_filename = sys.argv[1]
    if source_filename.endswith('.py'):
        json_dump_filename = source_filename[0:-3] + '.ast.json'
    else:
        raise ValueError('Invalid source filename {}.'.format(source_filename))

    with open(source_filename) as file:
        code = file.read()
        abstract_syntax_tree = ast.parse(code, source_filename)
        # visitor = Visitor()
        # print(visitor.visit(ast))
        babel_ast = create_babel_node(abstract_syntax_tree)
        print(babel_ast)
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
    sys.exit(1)
