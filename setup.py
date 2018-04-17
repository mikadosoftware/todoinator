{'<pkgname>': 'todoinator',
 '<rootdir>': '/home/pbrian/projects/todoinator2'}
#! -*- coding:utf-8 -*-

from setuptools import setup, find_packages

# get version data
with open("VERSION") as fo:
    version = fo.read()

setup(
     name='todoinator',
     version=version,
     description='ADescription to change',
     author='author',
     packages=find_packages(exclude=('tests')),
     entry_points={
         'console_scripts': ['todoinator=todoinator.cmdline:main']
     }
)

