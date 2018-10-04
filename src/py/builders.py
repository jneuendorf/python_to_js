import type_checkers as check


def identifier(name):
    return {
        'type': 'Identifier',
        'name': name,
    }


def string(value=''):
    return {
        'type': 'StringLiteral',
        'value': value,
        'extra': {
            'rawValue': value,
            # 'raw': '???'
        },
    }


def expression(expression):
    return {
        'type': 'ExpressionStatement',
        'expression': expression,
    }


def assignment(left, right, parenthesized=True):
    return expression({
        'type': 'AssignmentExpression',
        'operator': '=',
        'left': left,
        'right': right,
        'extra': {
            'parenthesized': parenthesized,
            # 'parenStart': 0,
        },
    })


# Corresponds to the 'Attribute' ast class.
def member_expression(object, property, computed=False):
    return {
        'type': 'MemberExpression',
        'object': object,
        'property': property,
        'computed': computed,
    }


def call_expression(callee, args=[], keywords=[], ensure_native_compatibility=True):
    plain_args = [
        (
            {'type': 'SpreadElement', 'argument': arg}
            if 'starred' in arg and arg['starred'] is True
            else arg
        )
        for arg in args
    ]
    plain_call_expression = {
        'type': 'CallExpression',
        'callee': callee,
        'arguments': plain_args,
    }

    if not ensure_native_compatibility:
        return plain_call_expression

    # else: if callee has '__def__' prop
    #       call like f(args, kwargs) otherwise like f(...args)
    return expression({
        'type': 'ConditionalExpression',
        # TODO: Use constant from 'JsHelperNames'
        'test': member_expression(
            object=callee,
            property=identifier('__def__')
        ),
        'consequent': {
            'type': 'CallExpression',
            'callee': callee,
            'arguments': [
                {
                    'type': 'ArrayExpression',
                    'elements': plain_args,
                },
                {
                    'type': 'ObjectExpression',
                    'properties': [
                        (
                            {'type': 'SpreadElement', 'argument': keyword['value']}
                            if keyword['arg'] is None
                            else object_property(
                                key=keyword['arg'],
                                value=keyword['value'],
                            )
                        )
                        for keyword in keywords
                    ],
                }
            ],
        },
        'alternate': plain_call_expression,
        'extra': {
            'parenthesized': True,
        },
    })


def array_destructuring(props, rest=None, bare_pattern=False, destructured=None, declare=None):
    array_pattern = {
        'type': 'ArrayPattern',
        'elements': [
            prop
            if not isinstance(prop, tuple)
            else {
                'type': 'AssignmentPattern',
                'left': prop[0],
                'right': prop[1]
            }
            for prop in props
        ]
        + (
            []
            if rest is None
            else [
                {
                    'type': 'RestElement',
                    'argument': rest,
                }
            ]
        )
    }

    if bare_pattern:
        return array_pattern

    if declare is None:
        return assignment(left=array_pattern, right=destructured)
    else:
        return {
            'type': 'VariableDeclaration',
            'declarations': [
                {
                    'type': 'VariableDeclarator',
                    'id': array_pattern,
                    'init': destructured,
                },
            ],
        }


UNDEFINED = tuple


# 'key' is ususally an identifier node.
# 'assignment' should be True for function definitions (default params).
def object_property(key, value=UNDEFINED, assignment=False):
    if value is UNDEFINED:
        value_node = key
    else:
        if assignment is True:
            value_node = {
                'type': 'AssignmentPattern',
                'left': key,
                'right': value
            }
        else:
            value_node = value

    return {
        'type': 'ObjectProperty',
        'method': False,
        'key': key,
        'computed': False,
        'shorthand': True,
        'value': value_node,
        'extra': {
            'shorthand': True,
        },
    }


def object_destructuring(props, rest=None, bare_pattern=False,
                         destructured=None, declare=None):
    '''Params:
    'destructured'       Str: The destructured object's name
    'props'     List<Str|Tuple<Str, babel_node>>
                e.g. [('a', numeric_literal(1)), 'b']
    'rest'      None => no rest
                Otherwise a string specifies the name of the identifier
    'declare'   None => expression:            ({a=1, ...b} = destructured)
                'let' => declaration:     let   {a=1, ...b} = destructured
                'const' => declaration:   const {a=1, ...b} = destructured
    '''

    object_pattern = {
        'type': 'ObjectPattern',
        'properties': [
            # {
            #     'type': 'ObjectProperty',
            #     'method': False,
            #     'key': (
            #         prop
            #         if not isinstance(prop, tuple)
            #         else prop[0]
            #     ),
            #     'computed': False,
            #     'shorthand': True,
            #     'value': (
            #         prop
            #         if not isinstance(prop, tuple)
            #         else {
            #             'type': 'AssignmentPattern',
            #             'left': prop[0],
            #             'right': prop[1]
            #         }
            #     ),
            #     'extra': {
            #         'shorthand': True,
            #     },
            # }
            (
                object_property(key=prop[0], value=prop[1], assignment=True)
                if isinstance(prop, tuple)
                else object_property(key=prop, value=UNDEFINED)
            )
            for prop in props
        ]
        + (
            []
            if rest is None
            else [
                {
                    'type': 'RestElement',
                    'argument': rest,
                }
            ]
        )
    }

    if bare_pattern:
        return object_pattern

    if declare is None:
        return destructured(left=object_pattern, right=destructured)
    else:
        return {
            'type': 'VariableDeclaration',
            'declarations': [
                {
                    'type': 'VariableDeclarator',
                    'id': object_pattern,
                    'init': destructured,
                },
            ],
        }


def object_expression(props, rest=None):
    return {
        'type': 'ObjectExpression',
        'properties': object_destructuring(props, rest, bare_pattern=True)['properties']
    }
