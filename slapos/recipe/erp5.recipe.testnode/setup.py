from setuptools import setup, find_packages

name = "erp5.recipe.testnode"
version = '1.0.23'

def read(name):
  return open(name).read()

long_description=( read('README.txt')
                   + '\n' +
                   read('CHANGES.txt')
                 )

setup(
    name = name,
    version = version,
    description = "ZC Buildout recipe for create an testnode instance",
    long_description=long_description,
    license = "GPLv3",
    keywords = "buildout erp5 test",
    classifiers=[
        "Framework :: Buildout :: Recipe",
        "Programming Language :: Python",
    ],
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    install_requires = [
      'setuptools',
      'slapos.lib.recipe',
      'xml_marshaller',
      'zc.buildout',
      'zc.recipe.egg',
      # below are requirements to provide full blown python interpreter
      'lxml',
      'PyXML',
      ],
    namespace_packages = ['erp5', 'erp5.recipe'],
    entry_points = {'zc.buildout': ['default = %s:Recipe' % name]},
    )
