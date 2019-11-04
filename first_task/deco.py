#!/usr/bin/env python
# -*- coding: utf-8 -*-

import functools
from pprint import pprint


def disable():
    '''
    Disable a decorator by re-assigning the decorator's name
    to this function. For example, to turn off memoization:

    >>> memo = disable

    '''
    return


def decorator(func):
    '''
    Decorate a decorator so that it inherits the docstrings
    and stuff from the function it's decorating.
    '''

    @functools.wraps(func)
    def get_doc_strings(*args, **kwargs):
        try:
            print(F"Function name: {func.__name__}")
            print(F"Docstring: {func.__doc__}")
            help(func)
            return func(*args, **kwargs)
        except Exception as e:
            pprint(e)

    return get_doc_strings


def countcalls(func):
    '''Decorator that counts calls made to the function decorated.'''
    @functools.wraps(func)
    def counter(*args):
        counter.calls = getattr(counter, 'calls', 0) + 1
        return func(*args)

    counter.calls = 0

    return counter


def memo(func):
    '''
    Memoize a function so that it caches all return values for
    faster future lookups.
    '''
    @functools.wraps(func)
    def cache(*args):
        (args) = args
        inner_func = func(*args)
        return inner_func

    return cache


def n_ary(func):
    '''
    Given binary function f(x, y), return an n_ary function such
    that f(x, y, z) = f(x, f(y,z)), etc. Also allow f(x) = x.
    '''

    @functools.wraps(func)
    def n_ary_func(x, *args):
        return x if not args else func(x, n_ary_func(*args))
    return n_ary_func


def trace():
    '''Trace calls made to function decorated.

    @trace("____")
    def fib(n):
        ....

    >>> fib(3)
     --> fib(3)
    ____ --> fib(2)
    ________ --> fib(1)
    ________ <-- fib(1) == 1
    ________ --> fib(0)
    ________ <-- fib(0) == 1
    ____ <-- fib(2) == 2
    ____ --> fib(1)
    ____ <-- fib(1) == 1
     <-- fib(3) == 3

    '''
    return


@countcalls
@memo
@n_ary
def foo(a, b):
    return a + b


@countcalls
@memo
@n_ary
def bar(a, b):
    return a * b


@countcalls
# @trace("####")
@memo
def fib(n):
    """Some doc"""
    return 1 if n <= 1 else fib(n-1) + fib(n-2)


def main():
    print(foo(4, 3))
    print(foo(4, 3))
    print(foo(4, 3))
    print("foo was called", foo.calls, "times")

    print(bar(4, 3))
    print(bar(4, 3))
    print(bar(4, 3))
    print("bar was called", bar.calls, "times")

    print(fib.__doc__)
    fib(3)
    print(fib.calls, 'calls made')


if __name__ == '__main__':
    main()
