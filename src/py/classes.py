import builders as build

import utils
from utils import consume


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
