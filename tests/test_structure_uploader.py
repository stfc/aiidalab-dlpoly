"""Tests for the StructureSelectionWidget."""

from alc_aiidalab_widgets.widgets import StructureViewWidget
from ipywidgets import HTML

from aiidalab_dlpoly.common.structure_uploader import StructureSelectionWidget


def test_construction():
    """A fresh widget exposes the import tabs and no selection."""
    widget = StructureSelectionWidget()
    assert widget.structure_data is None
    assert widget.structure_file is None
    assert widget.trajectory_data is None
    titles = [widget.tabs.get_title(i) for i in range(len(widget.tabs.children))]
    assert titles == ["Upload File", "AiiDA Database"]


def test_file_trait_dlinks_to_structure_file(xyz_bytes, xyz_singlefile):
    """The uploader's file trait is surfaced as structure_file.

    Mirrors a real upload where both ``file_dict`` and ``file`` are set: the
    former feeds the viewer, the latter is dlinked to ``structure_file``.
    """
    widget = StructureSelectionWidget()
    widget.file_uploader.file_dict = {"name": "water.xyz", "content": xyz_bytes}
    widget.file_uploader.file = xyz_singlefile
    assert widget.structure_file is xyz_singlefile


def test_file_upload_builds_viewer_from_bytes(xyz_bytes):
    """Uploading a file passes raw bytes to the viewer (regression test).

    Previously a BytesIO object was forwarded to the viewer which raised a
    TypeError inside alc_aiidalab_widgets; the uploader must hand over bytes.
    """
    widget = StructureSelectionWidget()
    widget.file_uploader.file_dict = {"name": "water.xyz", "content": xyz_bytes}

    widget._on_file_upload({"new": "water.xyz", "old": None})

    assert isinstance(widget.viewer, StructureViewWidget)
    assert widget.viewer in widget.children


def test_database_search_singlefile(xyz_singlefile):
    """Selecting a SinglefileData from the database sets structure_file."""
    widget = StructureSelectionWidget()

    widget._on_database_search({"new": xyz_singlefile, "old": None})

    assert widget.structure_file is xyz_singlefile
    assert widget.structure_data is None
    assert isinstance(widget.viewer, StructureViewWidget)


def test_database_search_structuredata(water_structure):
    """Selecting a StructureData from the database sets structure_data."""
    widget = StructureSelectionWidget()

    widget._on_database_search({"new": water_structure, "old": None})

    assert widget.structure_data is water_structure
    assert widget.structure_file is None
    assert isinstance(widget.viewer, StructureViewWidget)


def test_database_search_singlefile_clears_existing_structure(
    water_structure, xyz_singlefile
):
    """Selecting a file from the database clears a previous structure."""
    widget = StructureSelectionWidget()
    widget.structure_data = water_structure

    widget._on_database_search({"new": xyz_singlefile, "old": None})

    assert widget.structure_file is xyz_singlefile
    assert widget.structure_data is None


def test_database_search_structuredata_clears_existing_file(
    water_structure, xyz_singlefile
):
    """Selecting a structure from the database clears a previous file."""
    widget = StructureSelectionWidget()
    widget.structure_file = xyz_singlefile

    widget._on_database_search({"new": water_structure, "old": None})

    assert widget.structure_data is water_structure
    assert widget.structure_file is None


def test_database_search_unsupported_type_shows_message():
    """An unsupported node type falls back to the informational viewer."""
    from aiida.orm import Int
    from ipywidgets import HTML

    widget = StructureSelectionWidget()

    widget._on_database_search({"new": Int(1), "old": None})

    assert isinstance(widget.viewer, HTML)
    assert widget.structure_data is None
    assert widget.structure_file is None


def test_database_search_noop_when_unchanged(water_structure):
    """No update occurs when the selection is unchanged."""
    widget = StructureSelectionWidget()

    widget._on_database_search({"new": water_structure, "old": water_structure})

    assert widget.structure_data is None
    assert widget.structure_file is None


def test_create_viewer_with_none_shows_message():
    """A missing structure falls back to an informational HTML viewer."""
    widget = StructureSelectionWidget()

    widget._create_viewer(None)

    assert isinstance(widget.viewer, HTML)
    assert "Could not visualise" in widget.viewer.value


def test_disable_does_not_raise():
    """Disabling the widget tolerates children without a disable() method."""
    widget = StructureSelectionWidget()
    widget.disable(True)  # should not raise
