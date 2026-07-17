# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

sys.path.insert(0, os.path.abspath("../../src"))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "AiiDAlab DL_POLY"
copyright = "2026, STFC Daresbury Laboratory"
author = "Dr. Benjamin T. Speake"
release = "0.0.1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]

# The documentation is built in CI without the package's runtime dependencies
# installed, so mock the heavy third-party imports for autodoc.
autodoc_mock_imports = [
    "aiida",
    "aiidalab",
    "aiidalab_widgets_base",
    "alc_aiidalab_widgets",
    "ase",
    "home",
    "ipywidgets",
    "IPython",
    "plumpy",
    "traitlets",
    "weas_widget",
]

templates_path = ["_templates"]
exclude_patterns = []

source_suffix = ".rst"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "piccolo_theme"
html_static_path = ["_static"]
html_logo = "../../images/DL_Software_logo.png"
html_theme_options = {
    "source_url": "https://github.com/stfc/aiidalab-dlpoly",
}
