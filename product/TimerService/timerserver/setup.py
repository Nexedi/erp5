
modname = 'timerserver'
version = open('version.txt').read().strip()
numversion = version.split('.') 

license = 'GPL'
copyright = '''Nikolay Kim (c) 2004'''

author = "Nikolay Kim"
author_email = "fafhrd@legco.biz"

short_desc = "Timer Server for Zope"
long_desc = short_desc 

web = ""
ftp = ""
mailing_list = ""
#!/usr/bin/env python
import sys
try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup

setup(name='timerserver',
      version=version,
      license='GPL',
      description='Timer Server for Zope',
      long_description='',
      author='Nikolay Kim',
      author_email='fafhrd@legco.biz',
      packages=['timerserver'],
      zip_safe=False,
      package_data={'timerserver': ['component.xml']},
    )
