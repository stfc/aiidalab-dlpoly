"""Tests for the StructureInputModel MVC model."""

from aiidalab_dlpoly.models.structure import StructureInputModel


def test_defaults():
    """A fresh model holds no structure/file and is not submitted."""
    model = StructureInputModel()
    assert model.structure is None
    assert model.structure_file is None
    assert model.submitted is False
    assert model.has_structure is False
    assert model.has_file is False
    assert model.is_periodic is False


def test_has_structure(water_structure):
    """has_structure reflects an attached StructureData node."""
    model = StructureInputModel()
    model.structure = water_structure
    assert model.has_structure is True


def test_has_file(xyz_singlefile):
    """has_file reflects an attached SinglefileData node."""
    model = StructureInputModel()
    model.structure_file = xyz_singlefile
    assert model.has_file is True


def test_is_periodic_false_for_molecule(water_structure):
    """A non-periodic molecule reports is_periodic False."""
    model = StructureInputModel()
    model.structure = water_structure
    assert model.is_periodic is False


def test_is_periodic_true_for_bulk(periodic_structure):
    """A periodic bulk structure reports is_periodic True."""
    model = StructureInputModel()
    model.structure = periodic_structure
    assert model.is_periodic is True


def test_setting_structure_clears_file(water_structure, xyz_singlefile):
    """Assigning a StructureData clears any previously attached file."""
    model = StructureInputModel()
    model.structure_file = xyz_singlefile
    assert model.has_file is True

    model.structure = water_structure

    assert model.has_structure is True
    assert model.structure_file is None
    assert model.has_file is False
