"""Tests for the ComputationalResourcesModel."""

from aiidalab_dlpoly.models.resources import ComputationalResourcesModel


def test_defaults():
    """A fresh model has sensible defaults and is not submitted."""
    model = ComputationalResourcesModel()
    assert model.code_label == ""
    assert model.ncpus == 4
    assert model.process_label == ""
    assert model.process_description == ""
    assert model.submitted is False


def test_validate_requires_code():
    """Validation fails when no code has been selected."""
    model = ComputationalResourcesModel()
    assert model.validate() is False


def test_validate_passes_with_code():
    """Validation passes once a code label is set."""
    model = ComputationalResourcesModel()
    model.code_label = "dlpoly@localhost"
    assert model.validate() is True


def test_guide_mentions_dlpoly():
    """The guide text references DL_POLY."""
    assert "DL_POLY" in ComputationalResourcesModel.default_guide
