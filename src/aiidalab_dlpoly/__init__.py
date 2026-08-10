"""AiiDAlab application for DL_POLY molecular dynamics simulations."""

from importlib.metadata import PackageNotFoundError, version

try:
    # The version is defined once in setup.cfg (the single source of truth) and
    # read here from the installed package metadata.
    __version__ = version("aiidalab-dlpoly")
except PackageNotFoundError:
    # The package is not installed (e.g. running from a source checkout that has
    # not been installed); fall back to a placeholder.
    __version__ = "0.0.0"
