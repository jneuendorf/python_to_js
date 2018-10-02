export function print(args, kwargs) {
    console.log(...args)
}

// Preferring 'in' keyword.
// export const __has__ = (obj, prop) => obj.hasOwnProperty(prop)

export function __use_kwarg__(kwargs, prev_value, prop_name) {
    let new_value = prev_value
    if (kwargs.hasOwnProperty(prop_name)) {
        new_value = kwargs[prop_name]
        delete kwargs[prop_name]
    }
    return new_value
}

// Mark function as transpiled / not built-in.
// NOTE: Does not work when funciton is decorated...
export function __def__(func) {
    func.apply = (ctx, args, kwargs) => {
        return func.call(ctx, args, kwargs)
    }
}

// Add 'const self = this' for methods in order not to modify arguments additionally.
export function __call__(..._args) {
    let ctx, func, args, kwargs
    if (args.length === 4) {
        [ctx, func, args, kwargs] = _args
    }
    else {
        ctx = undefined
        [func, args, kwargs] = _args
    }
    // if (func.__def__) {
    //     return func.call(ctx, args, kwargs)
    // }
    // Native functions (their apply is also native) are called the normal way because
    // 'kwargs' is ignored
    return func.apply(ctx, args, kwargs)
}
