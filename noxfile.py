"""nox-poetry configuration file."""

from calcipy.dev.noxfile import (  # noqa: F401
    build_check, build_dist, check_safety, check_security, coverage, pin_dev_dependencies, tests,
)

# Ensure that non-calcipy dev-dependencies are available in Nox environments
pin_dev_dependencies(['bearboto3[s3]>=0.1.2', 'moto>=3.0.6', 'pydantic>=1.8.2'])
