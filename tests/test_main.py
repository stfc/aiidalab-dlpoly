"""Tests for the main application view and entry-point class."""

import ipywidgets as ipw

from aiidalab_dlpoly import main as main_module
from aiidalab_dlpoly.common.navigation import QuickAccessButtons
from aiidalab_dlpoly.main import MainApp, MainAppView
from aiidalab_dlpoly.process import MainAppModel
from aiidalab_dlpoly.wizards.main_app import MainAppWizardWidget


def _all_html(widget):
    """Recursively collect the HTML values within a widget tree."""
    values = []
    if isinstance(widget, ipw.HTML):
        values.append(widget.value)
    for child in getattr(widget, "children", ()):
        values.extend(_all_html(child))
    return values


def test_view_structure():
    """The view is a VBox holding the header, nav buttons, wizard and footer."""
    view = MainAppView(MainAppModel())
    assert isinstance(view, ipw.VBox)
    assert len(view.children) == 4
    assert isinstance(view.main, MainAppWizardWidget)


def test_view_contains_nav_buttons():
    """The header row includes the quick-access navigation buttons."""
    view = MainAppView(MainAppModel())
    assert any(isinstance(child, QuickAccessButtons) for child in view.children)


def test_view_contains_logo_and_title():
    """The header embeds the DL_Software logo and the app title."""
    html = "\n".join(_all_html(MainAppView(MainAppModel())))
    assert "DL_Software_logo.png" in html
    assert "AiiDAlab DL_POLY" in html


def test_main_app_displays_view(monkeypatch):
    """Instantiating MainApp builds a model/view and displays the view."""
    displayed = []
    monkeypatch.setattr(main_module, "display", displayed.append)

    app = MainApp()

    assert isinstance(app.model, MainAppModel)
    assert isinstance(app.view, MainAppView)
    assert displayed == [app.view]
