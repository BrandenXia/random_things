from collections.abc import Callable
from inspect import signature, Parameter
from typing import Any


def get_func_args[
    **P, R
](func: Callable[P, R],) -> tuple[dict[str, type], dict[str, tuple[type, Any]]]:
    """return the name, type of args and name, type, default value of kwargs of a function"""
    sig = signature(func)
    args: dict[str, type] = {}
    kwargs: dict[str, tuple[type, Any]] = {}

    for k, v in sig.parameters.items():
        if v.default is not Parameter.empty:
            kwargs[k] = (v.annotation, v.default)
        else:
            args[k] = v.annotation

    return args, kwargs
