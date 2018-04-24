#! -*- coding:utf-8 -*-

from setuptools import setup, find_packages

# get version data
with open("VERSION") as fo:
    semver = fo.read()

setup(
     name='todoinator',
     version=semver,
     description='Extract todo info from code.',
     author='Paul R. Brian <paul@mikadosoftware.com>',
     packages=find_packages(exclude=('tests')),
     scripts=['bin/todoinator']
)
