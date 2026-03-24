project = 'Nexus Documentation'
author = 'Nexus Team'
copyright = '2026, Nexus Team'
release = '0.1.0'

extensions = [
    'myst_parser',
    'sphinx_copybutton',
    'sphinx_design',
    'sphinx.ext.autodoc',  # API docs
    'sphinx.ext.intersphinx', # Links to PyTorch/NumPy docs
    'sphinx_copybutton',   # Adds "copy" to code blocks
    'sphinx_design',       # For cards/grids
    'sphinxcontrib.bibtex',# For research citations
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

bibtex_bibfiles = ["nexus-refs.bib"]

# -- Options for HTML output -------------------------------------------------
html_theme = 'furo'
html_title = "GT Nexus Docs"

html_static_path = ['_static']
html_css_files = ['custom.css']

html_theme_options = {
    'source_repository': 'https://github.com/gt-nexus/nexus-docs',
    'source_branch': 'main',
    'source_directory': '/',
    'navigation_with_keys': True,
    "light_css_variables": {
        # Sidebar and Top Bar
        "color-brand-primary": "#003057",    # GT Navy for navigation elements
        "color-brand-content": "#857437",    # Accessible Dark Gold for links/content
        
        # Sidebar background and text
        "color-sidebar-background": "#f9f6e5", # "Diploma" (GT light ivory)
        "color-sidebar-link-text": "#003057",
        
        # Admonitions (Notes, Tips, etc.)
        "color-admonition-title--note": "#B3A369", # Tech Gold
        "color-admonition-title-background--note": "rgba(179, 163, 105, 0.1)",
    },
    "dark_css_variables": {
        "color-brand-primary": "#B3A369",    # Gold stands out better in dark mode
        "color-brand-content": "#BFB37C",    # Lighter gold for better dark contrast
        
        "color-sidebar-background": "#002233", # "Atlanta Fog" (GT dark blue-black)
        "color-sidebar-link-text": "#FFFFFF",
    },
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
