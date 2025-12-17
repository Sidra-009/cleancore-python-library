import os
import sys
sys.path.insert(0, os.path.abspath('../../'))

project = 'Geomath-Python'
copyright = '2025, Sidra Saqlain'
author = 'Sidra Saqlain'
release = '0.2.1'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = []

# This is the "NumPy" look setting
html_theme = 'pydata_sphinx_theme'

html_static_path = ['_static']