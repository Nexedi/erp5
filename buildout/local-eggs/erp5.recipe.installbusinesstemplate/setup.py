# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

name = "erp5.recipe.installbusinesstemplate"
version = '0.1'

def read(name):
    return open(name).read()

long_description=(
        read('README.txt')
        + '\n' +
        read('CHANGES.txt')
    )

setup(
    name = name,
    version = version,
    author = "Nicolas Delaby",
    author_email = "nicolas@nexedi.com",
    description = "ZC Buildout recipe to install easily BT5 from repository",
    long_description=long_description,
    license = "ZPL 2.1",
    keywords = "zope2 buildout",
    classifiers=[
      "License :: OSI Approved :: Zope Public License",
      "Framework :: Buildout",
      "Framework :: Zope2",
      ],
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['erp5', 'erp5.recipe'],
    #install_requires = [
        #'infrae.subversion',
    #],
    zip_safe=False,
    entry_points = {'zc.buildout': ['default = %s:Recipe' % name]},
    )
