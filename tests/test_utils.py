"""Tests for the utility helpers."""

from IPython.display import Javascript

from aiidalab_dlpoly import utils


def test_open_link_in_new_tab(monkeypatch):
    """A JavaScript window.open call is displayed for the given path."""
    displayed = []
    monkeypatch.setattr(utils, "display", displayed.append)

    utils.open_link_in_new_tab("https://example.com/page")

    assert len(displayed) == 1
    assert isinstance(displayed[0], Javascript)
    assert "window.open('https://example.com/page', '_blank');" in displayed[0].data


def test_aiida_dlpoly_import_true():
    """The plugin is installed in the test environment."""
    assert utils.test_aiida_dlpoly_import() is True


def test_aiida_dlpoly_import_false(monkeypatch):
    """A missing plugin is reported as not installed."""

    def _raise(name):
        raise ImportError(name)

    monkeypatch.setattr(utils, "import_module", _raise)
    assert utils.test_aiida_dlpoly_import() is False


def test_aiida_dlpoly_import_reraises_other_errors(monkeypatch):
    """A non-ImportError during import is propagated, not swallowed."""

    def _raise(name):
        raise RuntimeError("boom")

    monkeypatch.setattr(utils, "import_module", _raise)
    try:
        utils.test_aiida_dlpoly_import()
    except RuntimeError as exc:
        assert str(exc) == "boom"
    else:
        raise AssertionError("expected RuntimeError to propagate")
