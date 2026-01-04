import os
import sys
sys.path.insert(0, os.path.abspath("../.."))

extensions = [
    "sphinx.ext.autodoc",
    "sphinx_autodoc_typehints",
]

html_theme = "sphinx_rtd_theme"
