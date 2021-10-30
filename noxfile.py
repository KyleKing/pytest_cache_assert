"""nox-poetry configuration file."""

from calcipy.dev.noxfile import (  # noqa: F401
    build_check, build_dist, check_safety, check_security, coverage, pin_dev_dependencies, tests,
)

# Ensure that non-calcipy dev-dependencies are available in Nox environments
pin_dev_dependencies(['pydantic>=1.8.2', 'cerberus>=1.3.4'])
