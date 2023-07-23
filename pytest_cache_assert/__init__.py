"""pytest_cache_assert."""

from enum import Enum
from os import getenv

from beartype import BeartypeConf
from beartype.claw import beartype_this_package
from typing_extensions import Self  # noqa: UP035

__version__ = '3.0.8'
__pkg_name__ = 'pytest_cache_assert'


class _BeartypeModes(Enum):
    """Supported global beartype modes."""

    ERROR = 'ERROR'
    WARNING = 'WARNING'
    OFF = None

    @classmethod
    def from_environment(cls) -> Self:
        """Return the configured mode."""
        beartype_mode = getenv('BEARTYPE_MODE') or None
        try:
            return cls(beartype_mode)
        except ValueError:
            msg = f"'BEARTYPE_MODE={beartype_mode}' is not an allowed mode from {[_e.value for _e in cls]}"
            raise ValueError(
                msg,
            ) from None


def configure_beartype() -> None:
    """Optionally configure beartype globally."""
    beartype_mode = _BeartypeModes.from_environment()

    if beartype_mode != _BeartypeModes.OFF:
        # PLANNED: Appease mypy and pyright, but this is a private import
        from beartype.roar._roarwarn import _BeartypeConfReduceDecoratorExceptionToWarningDefault
        beartype_warning_default = _BeartypeConfReduceDecoratorExceptionToWarningDefault

        beartype_this_package(conf=BeartypeConf(
            warning_cls_on_decorator_exception=(
                None if beartype_mode == _BeartypeModes.ERROR else beartype_warning_default
            ),
            is_color=getenv('BEARTYPE_NO_COLOR') is not None),
        )


configure_beartype()

# ====== Above is the recommended code from calcipy_template and may be updated on new releases ======

from ._check_assert.assert_config import AssertConfig  # noqa: E402,F401
from ._check_assert.assert_rules import (  # noqa: E402,F401
    AssertRule,
    Comparator,
    Wild,
    check_exact,
    check_suppress,
    check_type,
    gen_check_date_proximity,
    gen_check_date_range,
)
from ._check_assert.cache_store import CacheStoreType, LocalJSONCacheStore  # noqa: E402,F401
from ._check_assert.config import CacheAssertContainerKeys, register, retrieve  # noqa: E402,F401
from ._check_assert.converter import Converter  # noqa: E402,F401
from ._check_assert.error_message import NoCacheError  # noqa: E402,F401
from ._check_assert.validator import DictDiffValidator, ValidatorType  # noqa: E402,F401
