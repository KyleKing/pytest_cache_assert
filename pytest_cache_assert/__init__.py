"""pytest_cache_assert."""

import warnings

from beartype.roar import BeartypeDecorHintPepDeprecatedWarning
from loguru import logger

__version__ = '0.0.1'
__pkg_name__ = 'pytest_cache_assert'

logger.disable(__pkg_name__)

# Suppress Beartype warnings for now while 3.8.8 and below need to be supported
# See: https://github.com/beartype/beartype/issues/30#issuecomment-792176571
warnings.simplefilter(action='ignore', category=BeartypeDecorHintPepDeprecatedWarning)

# ====== Above is the recommended code from calcipy_template and may be updated on new releases ======
