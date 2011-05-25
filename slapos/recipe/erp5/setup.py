from setuptools import setup, find_packages

#def getGitIteration():
#  import subprocess
#  return str(int(subprocess.Popen(["git", "rev-list", "--count", "HEAD", "--",
#    "."], stdout=subprocess.PIPE).communicate()[0]))

name = "slapos.recipe.erp5"
version = '1.1-dev-184'

def read(name):
  return open(name).read()

long_description=( read('README.txt')
                   + '\n' +
                   read('CHANGES.txt')
                 )

setup(
    name = name,
    version = version,
    description = "ZC Buildout recipe for create an erp5 instance",
    long_description=long_description,
    license = "GPLv3",
    keywords = "buildout slapos erp5",
    classifiers=[
        "Framework :: Buildout :: Recipe",
        "Programming Language :: Python",
    ],
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    install_requires = [
      'zc.recipe.egg',
      'setuptools',
      'slapos.lib.recipe',
      'Zope2',
      ],
    namespace_packages = ['slapos', 'slapos.recipe'],
    entry_points = {'zc.buildout': ['default = %s:Recipe' % name]},
    )
