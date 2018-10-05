def _factory(type_str):
    type_str = type_str.capitalize()
    return lambda node={}: 'type' in node and node['type'] == type_str


is_identifier = _factory('identifier')

is_member_expression = _factory('MemberExpression')
is_call_expression = _factory('CallExpression')
