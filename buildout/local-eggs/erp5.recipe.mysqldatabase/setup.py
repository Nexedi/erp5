from setuptools import setup, find_packages

name = "erp5.recipe.mysqldatabase"
version = '1.0'

def read(name):
    return open(name).read()

long_description=( read('README.txt')
                   + '\n' +
                   read('CHANGES.txt')
                 )

setup(
    name = name,
    version = version,
    author = "Nexedi",
    author_email = "info@nexedi.com",
    description = "ZC Buildout recipe for create a mysql database",
    long_description=long_description,
    license = "ZPL 2.1",
    keywords = "zope2 buildout",
    url='http://www.erp5.org/HowToUseBuildout',
    classifiers=[
        "License :: OSI Approved :: Zope Public License",
        "Framework :: Buildout",
        "Framework :: Zope2",
        ],
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = ['zc.recipe.egg', ],
    namespace_packages = ['erp5', 'erp5.recipe'],
    entry_points = {'zc.buildout': ['default = %s:Recipe' % name]},
    ) 
