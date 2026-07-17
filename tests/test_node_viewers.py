"""Tests for the CustomAiidaNodeViewWidget."""

from aiida.orm import Int
from ipywidgets import DOMWidget

from aiidalab_dlpoly.common.node_viewers import CustomAiidaNodeViewWidget


def test_construction():
    """A fresh widget holds no node."""
    widget = CustomAiidaNodeViewWidget()
    assert widget.node is None


def test_viewer_for_structure(water_structure):
    """A StructureData resolves to a DOM (structure) viewer."""
    widget = CustomAiidaNodeViewWidget()
    viewer = widget._viewer(water_structure)
    assert isinstance(viewer, DOMWidget)


def test_viewer_for_singlefile(xyz_singlefile):
    """A SinglefileData resolves to a DOM viewer."""
    widget = CustomAiidaNodeViewWidget()
    viewer = widget._viewer(xyz_singlefile)
    assert isinstance(viewer, DOMWidget)


def test_viewer_for_process(finished_process_node):
    """A ProcessNode resolves to a DOM (process) viewer."""
    widget = CustomAiidaNodeViewWidget()
    viewer = widget._viewer(finished_process_node)
    assert isinstance(viewer, DOMWidget)


def test_viewer_fallback_returns_node():
    """A node with no registered viewer falls back to the node itself."""
    widget = CustomAiidaNodeViewWidget()
    node = Int(1).store()
    assert widget._viewer(node) is node


def test_setting_node_builds_and_caches_view(water_structure):
    """Assigning a node builds a viewer and caches it by uuid."""
    widget = CustomAiidaNodeViewWidget()
    widget.node = water_structure
    assert len(widget.children) == 1
    assert water_structure.uuid in widget.node_views


def test_cached_view_reused(water_structure, periodic_structure):
    """Re-selecting a previously viewed node reuses the cached widget."""
    widget = CustomAiidaNodeViewWidget()
    widget.node = water_structure
    cached = widget.node_views[water_structure.uuid]

    widget.node = periodic_structure
    widget.node = water_structure

    assert widget.children[0] is cached


def test_non_widget_view_uses_output():
    """A node without a widget viewer is displayed via the output area."""
    widget = CustomAiidaNodeViewWidget()
    widget.node = Int(1).store()
    assert widget._output in widget.children


def test_clearing_node_is_ignored(water_structure):
    """Setting the node back to None is a no-op."""
    widget = CustomAiidaNodeViewWidget()
    widget.node = water_structure
    built = widget.children

    widget.node = None

    assert widget.children is built


def test_process_type_fallback_to_base_mapping(monkeypatch, finished_process_node):
    """With no ALC/base node-type viewer, the process_type fallback is used."""
    import aiidalab_dlpoly.common.node_viewers as nv

    monkeypatch.setattr(nv, "ALC_AIIDA_VIEWER_MAPPING", {})
    monkeypatch.setattr(nv, "AIIDA_VIEWER_MAPPING", {})
    widget = CustomAiidaNodeViewWidget()

    # No viewer registered anywhere, so the node is returned as-is.
    assert widget._viewer(finished_process_node) is finished_process_node
