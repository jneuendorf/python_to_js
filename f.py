def f(a, b=1, *c, d, e=3, **f):
    print(a,b,c,d,e,f)

f(1,2,3,4,5,d='d')
# 1 2 (3, 4, 5) d 3 {}

f(1,b=2,c=(3,4,5),d='d')
# 1 2 () d 3 {'c': (3, 4, 5)}


# function f(args, kwargs) {
#     let [a, b=1, ...c] = args
#     let {d, e=3, ...f} = kwargs
#     // try to take all args from kwargs (except c because rest):
#     if (kwargs.hasOwnProperty('a')) a = kwargs.a
#     if (kwargs.hasOwnProperty('b')) b = kwargs.b
#     // If kwargs has an arg the arg cannot not also be in args because this would
#     // be a SyntaxError in python.
#     [a, b]
# }
# f([1,2,3,4,5], {d:'d'})
# f([1], {b:2, c: [3,4,5], d:'d'})
