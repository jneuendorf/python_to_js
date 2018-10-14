from collections import namedtuple


JsHelperNames = namedtuple('JsHelperNames', [
    # keys
    'INTERNAL_FUNC_CALL_FLAG',
    'GET_ARGS_AND_KWARGS',
    'CONSUME_KWARG_IF_POSSIBLE',
    'TUPLE_CONSTRUCTOR',
    'DICT_CONSTRUCTOR',
])(
    # values
    '__icall__',
    '__get_args__',
    '__use_kwarg__',
    'tuple',
    'dict',
)
