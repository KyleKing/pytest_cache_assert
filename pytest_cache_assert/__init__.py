"""pytest_cache_assert."""

from datetime import datetime, timezone
from enum import Enum
from os import getenv
from warnings import filterwarnings

from beartype import BeartypeConf
from beartype.claw import beartype_this_package
from beartype.roar import BeartypeDecorHintPep585DeprecationWarning
from typing_extensions import Self  # noqa: UP035

__version__ = '3.0.8'
__pkg_name__ = 'pytest_cache_assert'


class _RuntimeTypeCheckingModes(Enum):
    """Supported global runtime type checking modes."""

    ERROR = 'ERROR'
    WARNING = 'WARNING'
    OFF = None

    @classmethod
    def from_environment(cls) -> Self:  # pragma: no cover
        """Return the configured mode."""
        rtc_mode = getenv('RUNTIME_TYPE_CHECKING_MODE') or None
        try:
            return cls(rtc_mode)
        except ValueError:
            modes = [_e.value for _e in cls]
            msg = f"'RUNTIME_TYPE_CHECKING_MODE={rtc_mode}' is not an allowed mode from {modes}"
            raise ValueError(msg) from None


def configure_runtime_type_checking_mode() -> None:  # pragma: no cover
    """Optionally configure runtime type checking mode globally."""
    rtc_mode = _RuntimeTypeCheckingModes.from_environment()

    if rtc_mode is not _RuntimeTypeCheckingModes.OFF:
        from beartype.roar import BeartypeClawDecorWarning

        beartype_this_package(conf=BeartypeConf(
            warning_cls_on_decorator_exception=(
                None if rtc_mode is _RuntimeTypeCheckingModes.ERROR else BeartypeClawDecorWarning
            ),
        ))


_PEP585_DATE = 2025
if datetime.now(tz=timezone.utc).year <= _PEP585_DATE:  # pragma: no cover
    filterwarnings('ignore', category=BeartypeDecorHintPep585DeprecationWarning)
configure_runtime_type_checking_mode()

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
