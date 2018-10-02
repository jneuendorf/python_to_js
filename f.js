// def f(a, b=1, *c, d, e=3, **f):
//     print(a,b,c,d,e,f)
//
// f(1,2,3,4,5,d='d')
// # 1 2 (3, 4, 5) d 3 {}
//
// f(1,b=2,c=(3,4,5),d='d')
// # 1 2 () d 3 {'c': (3, 4, 5)}

function __use_kwarg__(kwargs, prev_value, prop_name) {
    let new_value = prev_value
    if (kwargs.hasOwnProperty(prop_name)) {
        new_value = kwargs[prop_name]
        delete kwargs[prop_name]
    }
    return new_value
}

__def__(function f([a, b=1, ...c], {d, e=3, ...f}) {
    // try to take all args from kwargs (except c because rest => '*c'):
    a = __use_kwarg__(f, a, 'a')
    b = __use_kwarg__(f, b, 'b')

    // If kwargs has an arg the arg cannot not also be in args because this would
    // be a SyntaxError in python.

    console.log(a,b,c,d,e,f)
})
// f([1,2,3,4,5], {d:'d'})
__call__(f, [1,2,3,4,5], {d:'d'})
// obj.f([1,2,3,4,5], {d:'d'})
__call__(obj, 'f', [1,2,3,4,5], {d:'d'})


// f([1], {b:2, c: [3,4,5], d:'d'})
