"""Collection of functional like tools"""
from typing import Iterable, Callable, Any, TypeVar, Dict
from functools import wraps

R = TypeVar("R")


def exactly_one_not_none(iterable_: Iterable) -> bool:
    """Is exactly one non-none element iny my iterable?"""
    return 1 == sum(list(map(lambda x: int(x) is not None, iterable_)))


def apply_on_non_none(iterable_: Iterable, callable_: Callable[..., R]) -> R:
    """If the iterable has exactly one non-none element: apply callable on it and return. Else raise exception"""
    element = None
    for i in iterable_:
        if i is not None:
            if element is not None:
                raise Exception("Invalid iterable: more than one non-none.")
            element = i
    if element is None:
        raise Exception("Invalid iterable: no non-none.")
    return callable_(element)
