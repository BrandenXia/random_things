from argparse import ArgumentParser
from collections.abc import Callable
from typing import Any

from rich_argparse import RichHelpFormatter

from .func import get_func_args


def conditional(value: str, condition: bool) -> tuple[str]:
    return (value,) if condition else ()


def to_flags(name: str) -> (str, str):
    return f"-{name[0]}", f"--{name}"


def add_arg(parser: ArgumentParser, name: str, type_: type, default: Any = None):
    name_or_flags = (name,) if default is None else to_flags(name)

    parser.add_argument(
        *name_or_flags,
        default=default,
        help=", ".join(
            [
                *conditional(
                    f"{type_.__name__ if hasattr(type_, "__name__") else type_}",
                    type_ != bool,
                ),
                *conditional(f"default is {repr(default)}", default is not None),
            ]
        ),
        action="store_true" if type_ == bool else None,
        **{"type": type_} if type_ != bool else {},
    )


def cli(func: Callable[..., Any]) -> Callable[..., Any]:
    parser = ArgumentParser(
        prog=func.__name__,
        description=func.__doc__,
        conflict_handler="resolve",
        formatter_class=RichHelpFormatter,
    )

    args, kwargs = get_func_args(func)
    for name, type_ in args.items():
        add_arg(parser, name, type_)
    for name, (type_, default) in kwargs.items():
        add_arg(parser, name, type_, default)

    def wrapper():
        cli_args = vars(parser.parse_args())
        func(**cli_args)

    return wrapper
