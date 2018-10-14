import builders as build

from utils import consume


@consume('id', 'ctx')
def map_name(babel_node, node, parents):
    # id = node.id
    # one of ast.Load, ast.Store, ast.Delete
    # ctx = node.ctx
    return build.identifier(node.id)
