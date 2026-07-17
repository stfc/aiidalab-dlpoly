"""Test the base python package (i.e. has it been installed correctly)."""

import importlib

import aiidalab_dlpoly


def test_version_defined():
    """The package exposes a non-empty version string."""
    assert aiidalab_dlpoly.__version__ is not None
    assert isinstance(aiidalab_dlpoly.__version__, str)


def test_submodules_importable():
    """All public submodules import cleanly."""
    for name in (
        "aiidalab_dlpoly.main",
        "aiidalab_dlpoly.process",
        "aiidalab_dlpoly.utils",
        "aiidalab_dlpoly.history",
        "aiidalab_dlpoly.models.structure",
        "aiidalab_dlpoly.models.workflow",
        "aiidalab_dlpoly.models.resources",
        "aiidalab_dlpoly.models.process",
        "aiidalab_dlpoly.models.results",
        "aiidalab_dlpoly.common.structure_uploader",
        "aiidalab_dlpoly.common.node_viewers",
        "aiidalab_dlpoly.common.navigation",
        "aiidalab_dlpoly.wizards.main_app",
        "aiidalab_dlpoly.wizards.structure",
        "aiidalab_dlpoly.wizards.workflow",
        "aiidalab_dlpoly.wizards.resources",
        "aiidalab_dlpoly.wizards.results",
    ):
        assert importlib.import_module(name) is not None
