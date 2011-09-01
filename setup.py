from setuptools import setup, find_packages
import glob
import os

version = '0.2-dev'
name = 'erp5.util'
long_description = open("README.erp5.util.txt").read() + "\n"

for f in sorted(glob.glob(os.path.join('erp5', 'util', 'README.*.txt'))):
  long_description += '\n' + open(f).read() + '\n'

long_description += open("CHANGES.erp5.util.txt").read() + "\n"

# silence setuptools, create README.txt
if not os.path.exists('README.txt'):
  os.symlink('README.erp5.util.txt', 'README.txt')

setup(name=name,
      version=version,
      description="ERP5 related utilities.",
      long_description=long_description,
      classifiers=[
          "Development Status :: 2 - Pre-Alpha",
          "Environment :: Console",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Operating System :: POSIX",
          "Programming Language :: Python",
          "Topic :: Utilities",
        ],
      url='http://www.erp5.org',
      author='The ERP5 Development Team',
      author_email='erp5-dev@erp5.org',
      keywords='erp5 utilities',
      license='GPLv3',
      namespace_packages=['erp5', 'erp5.util'],
      install_requires=[
        'setuptools', # namespaces
      ],
      extras_require={
        'testnode': ['slapos.core', 'xml_marshaller'],
        'test_browser': ['zope.testbrowser >= 3.11.1', 'z3c.etestbrowser'],
        'benchmark': [name+'[test_browser]'],
        'benchmark-report': [name+'[benchmark]', 'matplotlib', 'numpy'],
        'scalability_tester': [name+'[benchmark]', 'slapos.tool.nosqltester'],
      },
      zip_safe=True,
      packages=find_packages(),
      include_package_data=True,
      entry_points={
        'console_scripts': [
          'testnode = erp5.util.testnode:main [testnode]',
          'performance_tester_erp5 = erp5.util.benchmark.performance_tester:main [benchmark]',
          'scalability_tester_erp5 = erp5.util.benchmark.scalability_tester:main [scalability_tester]',
          'generate_erp5_tester_report = erp5.util.benchmark.report:generateReport [benchmark-report]',
        ],
      }
    )

# cleanup garbage
if os.path.islink('README.txt'):
  if os.readlink('README.txt') == 'README.erp5.util.txt':
    os.unlink('README.txt')
