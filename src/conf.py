import sys
from pathlib import Path

sys.path.append(str(Path('_ext').resolve()))

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "australorp.dev"
html_title = "australorp.dev"
html_baseurl = "australorp.dev"
copyright = '2025, Elias Prescott'
author = 'Elias Prescott'

blog_baseurl = html_baseurl
blog_title = "australorp.dev"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # custom
    'bible_ref',

    # built-in
    'sphinx.ext.githubpages',

    # third-party
    'ablog',
    'sphinxcontrib.youtube',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'
html_theme_options = {
    "secondary_sidebar_items": [],
    "icon_links": [
        {
            "name": "Atom Feed",
            "url": "/blog/atom.xml",
            "icon": "fa-solid fa-rss",
            "type": "fontawesome",
        },
    ],
}
html_static_path = ['_static']
