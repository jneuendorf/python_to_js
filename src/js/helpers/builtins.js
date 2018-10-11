export const print = __def__(function print(args, kwargs) {
    console.log(...args)
})

export function type() {
    // TODO
}

export const tuple = __def__(function tuple([iterable=[]], kwargs) {
    return Object.freeze([...iterable])
})

export const dict = __def__(function dict([iterable], kwargs) {
    // iterable = __use_kwarg__(kwargs, iterable, 'iterable')
    const map = new Map(iterable)
    for (const [key, value] of Object.entries(kwargs)) {
        map.set(key, value)
    }
    return new Proxy(map, {
        has(target, prop) {
            return target.has(prop)
        },
        get(target, prop) {
            if (['keys', 'values', 'entries', 'clear'].includes(prop)) {
                return target[prop].bind(target)
            }
            if (prop === 'items') {
                return target.entries.bind(target)
            }
            return target.get(prop)
        },
        set(target, prop, value) {
            return target.set(prop, value)
        },
        deleteProperty(target, prop) {
            return target.delete(prop)
        },
        ownKeys(target) {
            return [...target.keys()]
        }
    })
})

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
    func.__def__ = true
    // func.apply = (ctx, args, kwargs) => {
    //     return func.call(ctx, args, kwargs)
    // }
    // TODO: Maybe for convenience do this (but maybe it is better to stick to
    //       the JS environment and not provide pythonic features sometimes)
    // func.__name__ = func.name
    return func
}

// // Add 'const self = this' for methods in order not to modify arguments additionally.
// export function __call__(..._args) {
//     let ctx, func, args, kwargs
//     if (args.length === 4) {
//         [ctx, func, args, kwargs] = _args
//     }
//     else {
//         ctx = undefined
//         [func, args, kwargs] = _args
//     }
//     // if (func.__def__) {
//     //     return func.call(ctx, args, kwargs)
//     // }
//     // Native functions (their apply is also native) are called the normal way because
//     // 'kwargs' is ignored
//     return func.apply(ctx, args, kwargs)
// }
