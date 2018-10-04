# '''my nice docstring'''
#
# a = 1


# def func():
#     print('')
@dec1
@dec2(1, w=2)
def func(a, b=1, *c, d, e=3, **f):
    # print(a, b, c, d, e, f)
    pass

func(a, b=c, *d, **e)

# def func(a, b=1, *c):
#     # print(a, b, c)
#     pass


# class A():
#     pass


# class B(A):
#     pass
