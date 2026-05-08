"""Sphinx configuration for the GPEDC × IATI mapping documentation."""

from __future__ import annotations

import sys
from pathlib import Path

# Make the project source importable so autodoc can resolve gpedc_iati.*
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT))


# -- Project information ------------------------------------------------------

project = "gpedc-monitoring-mapping"
author = "GPEDC × IATI mapping contributors"
copyright = "2026"  # noqa: A001 — Sphinx convention
release = "0.1.0"


# -- General configuration ----------------------------------------------------

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_design",
]

source_suffix = {
    ".md": "markdown",
    ".rst": "restructuredtext",
}

master_doc = "index"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# MyST extensions for the kinds of markdown features we use
myst_enable_extensions = [
    "deflist",
    "fieldlist",
    "tasklist",
    "colon_fence",  # ::: directive blocks
    "smartquotes",
    "attrs_inline",
    "html_image",
]
myst_heading_anchors = 3


# -- Autodoc settings ---------------------------------------------------------

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
    "member-order": "bysource",
}
autodoc_typehints = "description"
autodoc_typehints_format = "short"
autodoc_member_order = "bysource"
napoleon_google_docstring = True
napoleon_numpy_docstring = False


# -- Intersphinx --------------------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "polars": ("https://docs.pola.rs/api/python/stable/", None),
}


# -- HTML output --------------------------------------------------------------

html_theme = "furo"
html_title = "GPEDC × IATI mapping"
html_static_path = ["_static"]

html_theme_options = {
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
    # Per-page "View source" / "Edit this page" links at the top of every
    # rendered page. Furo reads source_repository + source_branch + source_directory
    # to construct the GitHub URL for each .md file.
    "source_repository": "https://github.com/codywallace/gpedc-monitoring-mapping/",
    "source_branch": "main",
    "source_directory": "docs/",
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/codywallace/gpedc-monitoring-mapping",
            "html": (
                '<svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">'
                '<path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>'
                "</svg>"
            ),
            "class": "",
        },
    ],
}
