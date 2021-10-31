"""pytest_cache_assert."""

import warnings

from beartype.roar import BeartypeDecorHintPepDeprecatedWarning

from ._check_assert.key_rules import KeyRule, check_exact, check_suppress, check_type  # noqa: F401

__version__ = '0.0.1'
__pkg_name__ = 'pytest_cache_assert'

# Suppress Beartype warnings for now while 3.8.8 and below need to be supported
# See: https://github.com/beartype/beartype/issues/30#issuecomment-792176571
warnings.simplefilter(action='ignore', category=BeartypeDecorHintPepDeprecatedWarning)

# ====== Above is the recommended code from calcipy_template and may be updated on new releases ======
