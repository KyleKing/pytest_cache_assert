"""pytest_cache_assert."""

from ._check_assert.constants import Wildcards  # noqa: F401
from ._check_assert.key_rules import (  # noqa: F401
    Comparator, KeyRule, check_exact, check_suppress, check_type, gen_check_date_proximity, gen_check_date_range,
)

__version__ = '1.3.4'
__pkg_name__ = 'pytest_cache_assert'

# ====== Above is the recommended code from calcipy_template and may be updated on new releases ======
