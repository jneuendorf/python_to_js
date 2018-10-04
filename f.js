// def f(a, b=1, *c, d, e=3, **f):
//     print(a,b,c,d,e,f)
//
// f(1,2,3,4,5,d='d')
// # 1 2 (3, 4, 5) d 3 {}
//
// f(1,b=2,c=(3,4,5),d='d')
// # 1 2 () d 3 {'c': (3, 4, 5)}


__def__(function f([a, b=1, ...c], {d, e=3, ...f}) {
    // try to take all args from kwargs (except c because rest => '*c'):
    a = __use_kwarg__(f, a, 'a')
    b = __use_kwarg__(f, b, 'b')

    // If kwargs has an arg the arg cannot not also be in args because this would
    // be a SyntaxError in python.

    console.log(a,b,c,d,e,f)
})
// f([1,2,3,4,5], {d:'d'})
// f.apply(undefined, [1,2,3,4,5], {d:'d'})
f.__def__ ? f([1,2,3,4,5], {d:'d'}) : f(1,2,3,4,5)
// __call__(f, [1,2,3,4,5], {d:'d'})

// obj.f([1,2,3,4,5], {d:'d'})
// obj.f.apply(obj, [1,2,3,4,5], {d:'d'})
(obj.prop.f.__def__ ? obj.prop.f([1,2,3,4,5], {d:'d'}) : obj.prop.f(1,2,3,4,5))
// __call__(obj, 'f', [1,2,3,4,5], {d:'d'})


// f([1], {b:2, c: [3,4,5], d:'d'})

// (obj.prop.f.__def__ ? obj.prop.f(args, kwargs) : obj.prop.f(args_unpacked))
