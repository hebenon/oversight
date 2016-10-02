__author__ = 'bcarson'

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Oversight',
    'author': 'Ben Carson',
    'url': 'https://github.com/hebenon/oversight',
    'download_url': 'https://github.com/hebenon/oversight',
    'author_email': 'ben.carson@bigpond.com',
    'version': '0.1',
    'install_requires': ['nose', 'pillow', 'tensorflow'],
    'packages': ['oversight'],
    'scripts': [],
    'name': 'oversight'
}

setup(**config)
