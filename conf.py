project = 'Nexus Documentation'
author = 'Nexus Team'
copyright = '2026, Nexus Team'
release = '0.1.0'

extensions = [
    'myst_parser',
    'sphinx_copybutton',
    'sphinx_design',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'furo'
html_title = 'Nexus Documentation'
html_static_path = ['_static']
html_css_files = ['custom.css']
html_theme_options = {
    'source_repository': '',
    'source_branch': 'main',
    'source_directory': '/',
    'navigation_with_keys': True,
}

myst_enable_extensions = [
    'colon_fence',
    'deflist',
    'html_admonition',
    'html_image',
    'linkify',
    'substitution',
]

myst_heading_anchors = 3

nitpicky = False
