"""Tests for the AiiDAlab start banner."""

import importlib.util
from pathlib import Path

import ipywidgets as ipw

from aiidalab_dlpoly.common.navigation import QuickAccessButtons

# start.py lives at the repository root (outside the package), so load it by path.
_START_PATH = Path(__file__).parents[1] / "start.py"
_spec = importlib.util.spec_from_file_location("dlpoly_start", _START_PATH)
start = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(start)


def test_returns_vbox_with_logo_and_buttons():
    """The banner is a VBox holding the logo and the navigation buttons."""
    widget = start.get_start_widget("/apps/apps/dlpoly", "jup", "note")
    assert isinstance(widget, ipw.VBox)
    assert len(widget.children) == 2
    assert isinstance(widget.children[0], ipw.HTML)
    assert isinstance(widget.children[1], QuickAccessButtons)


def test_logo_links_to_main_and_uses_app_logo():
    """The logo image points at the app logo and links to the main notebook."""
    widget = start.get_start_widget("/apps/apps/dlpoly", "jup", "note")
    html = widget.children[0].value
    assert "DL_Software_logo.png" in html
    assert "/apps/apps/dlpoly/notebooks/main.ipynb" in html
