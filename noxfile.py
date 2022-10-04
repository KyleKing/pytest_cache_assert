"""nox-poetry configuration file."""

from calcipy.dev.noxfile import build_check, build_dist, coverage, pin_dev_dependencies, tests  # noqa: F401

# Ensure that non-calcipy dev-dependencies are available in Nox environments
pin_dev_dependencies(['hypothesis>=6.55.0', 'moto>=4.0.3', 'pendulum>=2.1.2', 'pytest-benchmark>=3.4.1'])
