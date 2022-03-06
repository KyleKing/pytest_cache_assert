"""Override the default validator for determining differences with the cached data."""

from implements import Interface, implements

try:
    from typing import Protocol, runtime_checkable
except ImportError:
    from typing_extensions import Protocol, runtime_checkable


class Validator(Interface):
    ...


@runtime_checkable
class ValidatorType(Protocol):
    ...


@implements(Validator)
class DiffValidator(ValidatorType):
    ...
