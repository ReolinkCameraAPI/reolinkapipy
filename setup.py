#!/usr/bin/python3
import os
import re
import codecs
from setuptools import setup, find_packages


def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


# Package meta-data.
NAME = 'reolinkapi'
DESCRIPTION = 'Reolink Camera API client written in Python 3'
URL = 'https://github.com/ReolinkCameraAPI/reolinkapipy'
AUTHOR_EMAIL = 'alanoterblanche@gmail.com'
AUTHOR = 'Benehiko'
LICENSE = 'GPL-3.0'
INSTALL_REQUIRES = [
    'setuptools',
    'PySocks==1.7.1',
    'PyYaml==6.0.2',
    'requests>=2.32.3',
]
EXTRAS_REQUIRE = {
    'streaming': [
        'numpy==2.0.1',
        'opencv-python==4.10.0.84',
        'Pillow==10.4.0',
    ],
}


here = os.path.abspath(os.path.dirname(__file__))
# read the contents of your README file
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name=NAME,
    python_requires='>=3.12.4',
    version=find_version('reolinkapi', '__init__.py'),
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=LICENSE,
    install_requires=INSTALL_REQUIRES,
    packages=find_packages(exclude=['examples', 'tests']),
    extras_require=EXTRAS_REQUIRE
)
