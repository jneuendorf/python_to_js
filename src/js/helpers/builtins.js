const {__def__} = require('./functions')


const print = __def__(function print(args, kwargs) {
    console.log(...args)
})

function type() {
    // TODO
}

const len = sequence => {
    if (typeof(sequence.__len__) === 'function') {
        return sequence.__len__()
    }
    if (typeof(sequence.length) === 'number') {
        return sequence.length
    }
    let size = 0
    for (const x of sequence) {
        size++
    }
    return size
}

const tuple = __def__(function tuple([iterable=[]], kwargs) {
    return Object.freeze([...iterable])
})

// Hm extending JS builtins only seems to work without a transpiler :(
// class dict extends Map {
//     constructor([iterable], kwargs) {
//         super(iterable)
//         for (const [key, value] of Object.entries(kwargs)) {
//             this.set(key, value)
//         }
//     }
//
//     static __call__(self, args, kwargs) {
//         return new dict(args, kwargs)
//     }
//
//     __len__() {
//         return this.size
//     }
//
//     __slice__(slice_type, key) {
//         if (slice_type === 'index') {
//             return this.get(key)
//         }
//         throw new Error('slicing is not supported for dicts (only sequential types).')
//     }
// }
class dict {
    constructor([iterable], kwargs) {
        this._map = new Map(iterable)
        for (const [key, value] of Object.entries(kwargs)) {
            this.set(key, value)
        }
    }

    static __call__(self, args, kwargs) {
        return new dict(args, kwargs)
    }

    __len__() {
        return this._map.size
    }

    __slice__(slice_type, key) {
        if (slice_type === 'index') {
            return this.get(key)
        }
        throw new Error('slicing is not supported for dicts (only sequential types).')
    }

    // Public methods. Calls to those are transpiled using __call__, thus we need
    // to use __def__ if we want to have support for kwargs.
    get(key) {
        return this._map.get(key)
    }

    set(key, value) {
        this._map.set(key, value)
    }
}

function set(iterable) {
    return new Set(iterable)
}


module.exports = {
    print,
    type,
    len,
    tuple,
    dict,
    set,
}
