#!/usr/bin/env python
from distutils.core import setup
from version import get_git_version

setup(
    name='slight',
    version=get_git_version(),
    packages=['slight'],
    url='http://codetalk.io/',
    license='BSD',
    author='Tehnix',
    author_email='christianlaustsen@gmail.com',
    description='Super Light Irresistible GitHub Tool... You know, like jenkins, only super light...'
)
