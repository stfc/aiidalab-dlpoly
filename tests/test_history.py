"""Tests for the process history application page."""

import ipywidgets as ipw

from aiidalab_dlpoly import history as history_module
from aiidalab_dlpoly.common.navigation import QuickAccessButtons
from aiidalab_dlpoly.history import HistoryApp, HistoryAppView, HistoryModel
from aiidalab_dlpoly.models.process import ProcessModel


def _all_html(widget):
    """Recursively collect the HTML values within a widget tree."""
    values = []
    if isinstance(widget, ipw.HTML):
        values.append(widget.value)
    for child in getattr(widget, "children", ()):
        values.extend(_all_html(child))
    return values


def test_history_model_is_process_model():
    """The history model extends the base process model."""
    assert isinstance(HistoryModel(), ProcessModel)


def test_view_structure():
    """The view is a VBox holding the header, controls and viewers."""
    view = HistoryAppView(HistoryModel())
    assert isinstance(view, ipw.VBox)
    assert len(view.children) == 8


def test_view_contains_logo_and_nav():
    """The header shows the logo and the navigation buttons."""
    view = HistoryAppView(HistoryModel())
    html = "\n".join(_all_html(view))
    assert "DL_Software_logo.png" in html
    assert any(isinstance(child, QuickAccessButtons) for child in view.children)


def test_update_node_view_sets_process_uuid(finished_process_node):
    """Selecting a node in the lookup widget updates the model uuid."""
    model = HistoryModel()
    view = HistoryAppView(model)
    view.lookup_widget.data_object = finished_process_node

    view._update_node_view(None)

    assert model.process_uuid == finished_process_node.uuid


def test_update_node_view_ignores_none():
    """No update occurs when no node is selected."""
    model = HistoryModel()
    view = HistoryAppView(model)

    view._update_node_view(None)

    assert model.process_uuid is None


def test_history_app_displays_view(monkeypatch):
    """Instantiating HistoryApp builds a model/view and displays the view."""
    displayed = []
    monkeypatch.setattr(history_module, "display", displayed.append)

    app = HistoryApp()

    assert isinstance(app.model, HistoryModel)
    assert isinstance(app.view, HistoryAppView)
    assert displayed == [app.view]
