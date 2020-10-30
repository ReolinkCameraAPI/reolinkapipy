#!/usr/bin/python3

import os
import re
import codecs
from setuptools import setup

# Package meta-data.
NAME = 'reolink-api'
DESCRIPTION = 'Reolink Camera API written in Python 3.6'
URL = 'https://github.com/Benehiko/ReolinkCameraAPI'
AUTHOR_EMAIL = ''
AUTHOR = 'Benehiko'
LICENSE = 'GPL-3.0'
INSTALL_REQUIRES = [
    'pillow',
    'pyyaml',
    'requests>=2.18.4',
    'numpy',
    'opencv-python',
    'pysocks'
]


here = os.path.abspath(os.path.dirname(__file__))
# read the contents of your README file
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(name=NAME,
      python_requires='>=3.6.0',
      version=find_version('api', '__init__.py'),
      description=DESCRIPTION,
      long_description=long_description,
      long_description_content_type='text/markdown',
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      url=URL,
      license=LICENSE,
      install_requires=INSTALL_REQUIRES,
      py_modules=[
          'Camera',
          'ConfigHandler',
          'RtspClient',
          'resthandle',
          'api.APIHandler',
          'api.device',
          'api.display',
          'api.network',
          'api.ptz',
          'api.recording',
          'api.system',
          'api.user',
          'api.zoom',
          'api.alarm',
          'api.image'
      ]
      )
