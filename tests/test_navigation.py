"""Tests for the QuickAccessButtons navigation widget."""

import ipywidgets as ipw

import aiidalab_dlpoly.common.navigation as navigation
from aiidalab_dlpoly.common.navigation import QuickAccessButtons


def _patched_buttons(monkeypatch):
    """Build a QuickAccessButtons whose links capture their target URL."""
    calls = []
    monkeypatch.setattr(
        navigation, "open_link_in_new_tab", lambda path, _=None: calls.append(path)
    )
    return QuickAccessButtons(), calls


def test_construction_has_four_buttons():
    """The widget exposes four navigation buttons."""
    buttons = QuickAccessButtons()
    assert isinstance(buttons, ipw.HBox)
    assert len(buttons.children) == 4
    assert all(isinstance(child, ipw.Button) for child in buttons.children)


def test_button_labels():
    """The buttons carry the expected labels."""
    buttons = QuickAccessButtons()
    labels = [child.description for child in buttons.children]
    assert labels == [
        "New Calculation",
        "History",
        "Setup Resources",
        "Documentation",
    ]


def test_new_calculation_link(monkeypatch):
    """New Calculation opens the main notebook."""
    buttons, calls = _patched_buttons(monkeypatch)
    buttons.new_calc_link.click()
    assert calls == ["/apps/apps/dlpoly/notebooks/main.ipynb"]


def test_history_link(monkeypatch):
    """History opens the history notebook."""
    buttons, calls = _patched_buttons(monkeypatch)
    buttons.history_link.click()
    assert calls == ["/apps/apps/dlpoly/notebooks/history.ipynb"]


def test_resource_setup_link(monkeypatch):
    """Setup Resources opens the resources notebook."""
    buttons, calls = _patched_buttons(monkeypatch)
    buttons.resource_setup_link.click()
    assert calls == ["/apps/apps/dlpoly/notebooks/resources.ipynb"]


def test_documentation_link(monkeypatch):
    """Documentation opens the project repository."""
    buttons, calls = _patched_buttons(monkeypatch)
    buttons.docs_link.click()
    assert calls == ["https://github.com/stfc/aiidalab-dlpoly"]
