from typing import Any, ParamSpec, TypeVar

T = TypeVar("T")
K = TypeVar("K")
P = ParamSpec("P")

Row = TypeVar("Row", bound=tuple[Any, ...])
