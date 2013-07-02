#!/usr/bin/env python

from setuptools import setup

PACKAGE = 'pmmm'

setup(name=PACKAGE,
      description='Project management module for Mercurial. Creates and manages project-wise shared repositories and allow each person to manage her own.',
      keywords='trac plugin project management',
      version='0.5',
      url='',
      license='http://www.opensource.org/licenses/mit-license.php',
      author='Haobo Yu',
      author_email='haoboy@rytong.net',
      long_description="""
      """,
      packages=[PACKAGE],
      package_data={PACKAGE : ['templates/*.cs', 'templates/*.html', 'htdocs/*.css', 'htdocs/*.png', 'htdocs/*.js']},
      entry_points={'trac.plugins': '%s = %s' % (PACKAGE, PACKAGE)})

#### AUTHORS ####
## Primary Author:
## Haobo Yu
## http://www.rytong.net/
## haoboy@rytong.net
## trac-hacks user: haoboy

