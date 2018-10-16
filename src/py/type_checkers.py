import utils


def _factory(type_str):
    type_str = type_str.capitalize()
    return lambda node: 'type' in node and node['type'] == type_str


is_identifier = _factory('identifier')

is_member_expression = _factory('MemberExpression')
_is_call_expression = _factory('CallExpression')


def is_call_expression(node, regard_wrapped=True):
    if _is_call_expression(node):
        return True
    return is_wrapped_call_expression(node) if regard_wrapped else False


def is_wrapped_call_expression(node):
    '''Corresponds to 'call_expression(ensure_native_compatibility=True)'.'''
    return utils.shape(
        node,
        'expression.condition_expression__alternate.call_expression'
    )
