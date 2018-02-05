#!/usr/bin/env python
try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup

setup(name='timerserver',
      version='2.0.4',
      license='GPL',
      description='Timer Server for Zope',
      long_description='',
      author='Nikolay Kim',
      author_email='fafhrd@legco.biz',
      packages=['timerserver'],
      zip_safe=False,
      package_data={'timerserver': ['component.xml']},
    )
