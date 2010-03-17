from setuptools import setup, find_packages

name = "erp5.recipe.standaloneinstance"
version = '0.3'

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
    author = "Lukasz Nowak",
    author_email = "luke@nexedi.com",
    description = "ZC Buildout recipe to install standalone instance",
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
    install_requires = [
        'plone.recipe.zope2instance',
        'erp5.recipe.mysqldatabase',
    ],
    zip_safe=False,
    entry_points = {'zc.buildout': ['default = %s:Recipe' % name]},
    )
