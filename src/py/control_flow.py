import builders as build


def map_continue(babel_node, node, parents):
    return {
        'type': 'ContinueStatement',
    }


def map_break(babel_node, node, parents):
    return {
        'type': 'BreakStatement',
    }


def map_if(babel_node, node, parents):
    test = babel_node['test']
    body = babel_node['body']
    orelse = babel_node['orelse']
    return build.if_statement(
        test=test,
        consequent=body,
        alternate=orelse if orelse else None,
    )


def map_for(babel_node, node, parents):
    target = babel_node['target']
    iter = babel_node['iter']
    body = babel_node['body']
    orelse = babel_node['orelse']
