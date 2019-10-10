from setuptools import setup, find_packages
import glob
import os

version = '0.4.63'
name = 'erp5.util'
long_description = open("README.erp5.util.txt").read() + "\n"

for f in sorted(glob.glob(os.path.join('erp5', 'util', 'README.*.txt'))):
  long_description += '\n' + open(f).read() + '\n'

long_description += open("CHANGES.erp5.util.txt").read() + "\n"

# silence setuptools, create README.txt
if not os.path.exists('README.txt'):
  os.symlink('README.erp5.util.txt', 'README.txt')

benchmark_install_require_list = [name+'[testbrowser]']

# argparse needed for erp5.util.benchmark is only available from python >= 2.7
import sys
python_major_version, python_minor_version = sys.version_info[:2]
if python_major_version == 2 and python_minor_version < 7:
  benchmark_install_require_list.append('argparse')

# Only build/install erp5.util package, otherwise other directories may
# be considered as part of erp5.util (such as product)
package_list = ['erp5.%s' % subpackage for subpackage in find_packages('erp5')]
package_list.append('erp5')

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
      url='http://www.erp5.com',
      author='The ERP5 Development Team',
      keywords='erp5 utilities',
      license='GPLv3',
      namespace_packages=['erp5', 'erp5.util'],
      install_requires=[
        'setuptools', # namespaces
        'psutil >= 0.5.0',
        'six',
      ],
      extras_require={
        'testnode': ['slapos.core', 'xml_marshaller', 'psutil >= 0.5.0'],
        'testbrowser': ['zope.testbrowser >= 5.0.0', 'z3c.etestbrowser'],
        'benchmark': benchmark_install_require_list,
        'benchmark-report': [name+'[benchmark]', 'matplotlib', 'numpy'],
        'scalability_tester': [name+'[benchmark]', 'slapos.tool.nosqltester'],
        'zodbanalyse': ['ZODB'],
      },
      zip_safe=True,
      packages=package_list,
      include_package_data=True,
      entry_points={
        'console_scripts': [
          'testnode = erp5.util.testnode:main [testnode]',
          'performance_tester_erp5 = '\
            'erp5.util.benchmark.performance_tester:main [benchmark]',
          'scalability_tester_erp5 = '\
            'erp5.util.benchmark.scalability_tester:main [scalability_tester]',
          'runScalabilityTestSuite = '\
            'erp5.util.scalability.runScalabilityTestSuite:main',
          'requestUrl = '\
            'erp5.util.scalability.requestUrl:main',
          'generate_erp5_tester_report = '\
            'erp5.util.benchmark.report:generateReport [benchmark-report]',
          'web_checker_utility = erp5.util.webchecker:web_checker_utility'
        ],
      },
      test_suite='erp5.tests',
      tests_require=[
        'slapos.core',
        'xml_marshaller',
        'psutil >= 0.5.0',
        'mock; python_version < "3"',
      ],
    )

# cleanup garbage
if os.path.islink('README.txt'):
  if os.readlink('README.txt') == 'README.erp5.util.txt':
    os.unlink('README.txt')
