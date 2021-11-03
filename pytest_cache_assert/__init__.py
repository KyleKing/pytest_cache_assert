"""pytest_cache_assert."""

import warnings

from beartype.roar import BeartypeDecorHintPepDeprecatedWarning

from ._check_assert.constants import DEF_CACHE_DIR_KEY, DEF_CACHE_DIR_NAME, Wildcards  # noqa: F401
from ._check_assert.key_rules import KeyRule, check_exact, check_suppress, check_type  # noqa: F401

__version__ = '1.0.0'
__pkg_name__ = 'pytest_cache_assert'

# Suppress Beartype warnings for now while 3.8.8 and below need to be supported
# See: https://github.com/beartype/beartype/issues/30#issuecomment-792176571
warnings.simplefilter(action='ignore', category=BeartypeDecorHintPepDeprecatedWarning)

# ====== Above is the recommended code from calcipy_template and may be updated on new releases ======
