"""Contains utility functions used throughout the python package."""

from importlib import import_module

from IPython.display import Javascript, display


def open_link_in_new_tab(path: str, _=None) -> None:
    """
    Open a given link in a new browser tab.

    Parameters
    ----------
    path :  str
        The link to be opened.
    """
    js_code = f"window.open('{path}', '_blank');"
    display(Javascript(js_code))
    return


def test_aiida_dlpoly_import() -> bool:
    """
    Test if the aiida-dlpoly plugin is installed.

    Returns
    -------
    bool
        True if the aiida-dlpoly plugin is installed, False otherwise.
    """
    try:
        import_module("aiida_dlpoly")
    except ImportError:
        return False
    except Exception as e:
        raise e
    else:
        return True
