import ast

from utils import consume


@consume('targets', 'value')
def _map_assign(babel_node, node, parents):
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
def _map_assign_to_class_prop(babel_node, node, parents):
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


def map_assign(babel_node, node, parents):
    if parents and isinstance(parents[0], ast.ClassDef):
        return _map_assign_to_class_prop(babel_node, node, parents)
    else:
        return _map_assign(babel_node, node, parents)
