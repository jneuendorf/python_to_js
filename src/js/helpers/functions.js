// Mark function as transpiled / not built-in.
// NOTE: Does not work when funciton is decorated...
function __def__(func) {
    func.__def__ = true
    // func.__call__ = func.call
    // func.call = (ctx, ...__arguments__) => {
    //     const args = __arguments__.slice(0, -1)
    //     const kwargs = __arguments__.slice(-1)[0]
    //     return func.__call__(ctx, args, kwargs, '__icall__')
    // }
    // func.apply = (ctx, args, kwargs) => {
    //     return func.call(ctx, args, kwargs)
    // }
    func.__call__ = (ctx, args, kwargs) => {
        return func.call(ctx, args, kwargs, '__icall__')
    }
    // TODO: Maybe for convenience do this (but maybe it is better to stick to
    //       the JS environment and not provide pythonic features sometimes)
    // func.__name__ = func.name
    return func
}

// This helper is needed in case a transpiled function gets called from a non-transpiled
// function. In this case the transpiled function could be called without any arguments
// thus destructuring right in the signature would not work.
const __get_args__ = args => {
    // args[2] must be JsHelperNames.INTERNAL_FUNC_CALL_FLAG
    if (args.length === 3 && args[2] === '__icall__') {
        return [args[0], args[1]]
    }
    else {
        return [args, {}]
    }
}

function __use_kwarg__(kwargs, prev_value, prop_name) {
    let new_value = prev_value
    if (kwargs.hasOwnProperty(prop_name)) {
        new_value = kwargs[prop_name]
        delete kwargs[prop_name]
    }
    return new_value
}

function __call__(ctx, key_or_callable, ...__arguments__) {
    const args = __arguments__.slice(0, -1)
    const kwargs = __arguments__.slice(-1)[0]
    const callable = (
        ctx
        ? ctx[key_or_callable]
        : key_or_callable
    )

    if (!callable) {
        console.debug('DEBUG:', ctx, key_or_callable)
    }

    if (callable.__call__) {
        return callable.__call__(ctx, args, kwargs)
    }
    // Call native function normally.
    return callable.apply(ctx, args)
}


module.exports = {
    __def__,
    __get_args__,
    __use_kwarg__,
    __call__,
}
