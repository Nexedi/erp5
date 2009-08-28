#!/usr/bin/python2.4
import os
import sys
import pdb
import re
import getopt
import unittest
import shutil
import errno

WIN = os.name == 'nt'


__doc__ = """%(program)s: unit test runner for the ERP5 Project

usage: %(program)s [options] [UnitTest1[.TestClass1[.testMethod]] [...]]

Options:
  -v, --verbose              produce verbose output
  -h, --help                 this help screen
  -p, --profile              print profiling results at the end
  --portal_id=STRING         force id of the portal. Useful when using
                             --data_fs_path to run tests on an existing
                             Data.fs
  --data_fs_path=STRING      Use the given path for the Data.fs
  --bt5_path                 Path to the Business Templates. Default is
                             INSTANCE_HOME/bt5.
  --recreate_catalog=0 or 1  recreate the content of the sql catalog. Default
                             is to recreate, unless using --data_fs_path
  --save                     Run unit tests in persistent mode (if unset,
                             existing Data.fs, dump.sql and *.bak static
                             folders are not modified). Tests are skipped
                             if business templates are updated
                             or if --load is unset.
  --load                     Reuse existing instance (created with --save).
  --erp5_sql_connection_string=STRING
                             ZSQL Connection string for erp5_sql_connection, by
                             default, it will use "test test"
  --cmf_activity_sql_connection_string=STRING
                             ZSQL Connection string for
                             cmf_activity_sql_connection (if unset, defaults to
                             erp5_sql_connection_string)
  --erp5_sql_deferred_connection_string=STRING 
                             ZSQL Connection string for
                             erp5_sql_deferred_connection (if unset, defaults
                             to erp5_sql_connection_string)
  --email_from_address=STRING
                             Initialise the email_from_address property of the
                             portal, by default, CMFActivity failures are sent
                             on localhost from this address, to this address
  --erp5_catalog_storage=STRING
                             Use the given business template as erp5_catalog
                             dependency provider (ie, the name of the BT
                             containing ZSQLMethods matching the desired
                             catalog storage).
  --run_only=STRING
                             Run only specified test methods delimited with
                             commas (e.g. testFoo,testBar). This can be regular
                             expressions.
  -D
                             Invoke debugger on errors / failures.
  --update_business_templates
                             Update all business templates prior to runing
                             tests. This only has a meaning when doing
                             upgratability checks, in conjunction with --load.
                             --update_only can be use to restrict the list of
                             templates to update.
  --update_only=STRING
                             Specify the list of business template to update if
                             you don't want to update them all. You can give a list
                             delimited with commas (e.g. erp5_core,erp5_xhtml_style).
                             This can be regular expressions. 
"""

def getUnitTestFile():
  """returns the absolute path of this script.
  This is used by template tool to run unit tests."""
  return os.path.abspath(__file__)


def initializeInstanceHome(tests_framework_home,
                           real_instance_home,
                           instance_home):
  if not os.path.exists(instance_home):
    os.mkdir(instance_home)

  # Before r23751, Extensions dir was initialized to be a symlink to real
  # instance home Extensions folder, now it's initialized as an independant
  # folder. If this test instance still have a symlink for Extensions, change
  # it in a foler.
  extensions_path = os.path.join(instance_home, 'Extensions')
  if os.path.islink(extensions_path):
    os.unlink(extensions_path)

  for d in ('Extensions', 'Constraint', 'Document', 'PropertySheet', 'bin', 'etc', 'tests', 'var', 'log'):
    path = os.path.join(instance_home, d)
    if not os.path.exists(path):
      os.mkdir(path)
  for d in ('Products', 'bt5', 'svn', 'lib'):
    src = os.path.join(real_instance_home, d)
    dst = os.path.join(instance_home, d)
    if not os.path.exists(dst):
      if os.path.islink(dst):
        os.unlink(dst)
      if WIN:
        if d in ('Products', 'bt5', 'svn'):
          os.mkdir(dst)
        else:
          shutil.copytree(src, dst)
      else:
        os.symlink(src, dst)
  src = os.path.join(tests_framework_home, 'custom_zodb.py')
  dst = os.path.join(instance_home, 'custom_zodb.py')
  if not os.path.exists(dst):
    if os.path.islink(dst):
      os.unlink(dst)
    if WIN:
      shutil.copy(src, dst)
    else:
      os.symlink(src, dst)
  # add some paths where we can find copyzopeskel
  sys.path.append(os.path.join(zope_home, "bin"))
  sys.path.append(os.path.join(zope_home, "utilities"))
  import copyzopeskel
  kw = {
    "PYTHON":sys.executable,
    "INSTANCE_HOME": instance_home,
    "SOFTWARE_HOME": software_home,
    "ZOPE_HOME": zope_home,
    }
  skelsrc = os.path.abspath(os.path.join(os.path.dirname(__file__), "skel"))
  copyzopeskel.copyskel(skelsrc, instance_home, None, None, **kw)

# site specific variables
tests_framework_home = os.path.dirname(os.path.abspath(__file__))

# find zope home, either from SOFTWARE_HOME environment variable, or by
# guessing some common paths.
if 'SOFTWARE_HOME' in os.environ:
  software_home = os.environ['SOFTWARE_HOME']
  if not os.path.exists(software_home):
    raise ValueError('SOFTWARE_HOME is set to non existing directory %r'
                      % (software_home,))
  # software_home is zope_home/lib/python, remove lib/python
  zope_home = os.path.split(os.path.split(software_home)[0])[0]
else:
  if WIN:
    erp5_home = os.path.sep.join(
        tests_framework_home.split(os.path.sep)[:-4])
    zope_home = os.path.join(erp5_home, 'Zope')
  elif os.path.isdir('/usr/lib64/zope/lib/python'):
    zope_home = '/usr/lib64/zope'
  elif os.path.isdir('/usr/lib/erp5/lib/python'):
    zope_home = '/usr/lib/erp5'
  elif os.path.isdir('/usr/lib/zope2.8/lib/python'):
    zope_home = '/usr/lib/zope2.8'
  else:
    zope_home = '/usr/lib/zope'
  software_home = os.path.join(zope_home, 'lib', 'python')

# handle 'system global' instance and windows
if WIN:
  real_instance_home = os.path.join(erp5_home, 'ERP5Instance')
elif tests_framework_home.startswith('/usr/lib'):
  if os.path.isdir('/var/lib/erp5'):
    real_instance_home = '/var/lib/erp5'
  else:
    real_instance_home = '/var/lib/zope'
else:
  real_instance_home = os.path.sep.join(
      tests_framework_home.split(os.path.sep)[:-3])

instance_home = os.path.join(real_instance_home, 'unit_test')
real_tests_home = os.path.join(real_instance_home, 'tests')
tests_home = os.path.join(instance_home, 'tests')

initializeInstanceHome(tests_framework_home, real_instance_home, instance_home)

if '__INSTANCE_HOME' not in globals().keys() :
  __INSTANCE_HOME = instance_home


class ERP5TypeTestLoader(unittest.TestLoader):
  """Load test cases from the name passed on the command line.
  """
  def loadTestsFromName(self, name, module=None):
    """This method is here for compatibility with old style arguments.
    - It is possible to have the .py prefix for the test file
    - It is possible to separate test classes with : instead of .
    """
    # backward compatibility 
    if name.endswith('.py'):
      name = name[:-3]
    name = name.replace(':', '.')
    return unittest.TestLoader.loadTestsFromName(self, name, module)

  def loadTestsFromModule(self, module):
    """ERP5Type test loader supports a function named 'test_suite'
    """
    if hasattr(module, 'test_suite'):
      return module.test_suite()
    return unittest.TestLoader.loadTestsFromModule(self, module)


class DebugTestResult:
  """Wrap an unittest.TestResult, invoking pdb on errors / failures
  """
  def __init__(self, result):
    self.result = result

  def _start_debugger(self, tb):
    try:
      # try ipython if available
      import IPython
      IPython.Shell.IPShell(argv=[])
      p = IPython.Debugger.Pdb(color_scheme=__IPYTHON__.rc.colors)
      p.reset()
      while tb.tb_next is not None:
        tb = tb.tb_next
      p.interaction(tb.tb_frame, tb)
    except ImportError:
      pdb.post_mortem(tb)

  def addError(self, test, err):
    self._start_debugger(err[2])
    self.result.addError(test, err)

  def addFailure(self, test, err):
    self._start_debugger(err[2])
    self.result.addFailure(test, err)

  def __getattr__(self, attr):
    return getattr(self.result, attr)


def runUnitTestList(test_list, verbosity=1, debug=0):
  if not test_list:
    print "No test to run, exiting immediately."
    return
  os.environ.setdefault('INSTANCE_HOME', instance_home)
  os.environ.setdefault('SOFTWARE_HOME', software_home)
  os.environ.setdefault('COPY_OF_INSTANCE_HOME', instance_home)
  os.environ.setdefault('COPY_OF_SOFTWARE_HOME', software_home)
  os.environ.setdefault('EVENT_LOG_FILE', os.path.join(tests_home, 'zLOG.log'))
  os.environ.setdefault('EVENT_LOG_SEVERITY', '-300')

  execfile(os.path.join(tests_framework_home, 'framework.py'),
              dict(__name__='__main__'))
  
  if WIN:
    products_home = os.path.join(real_instance_home, 'Products')
    import Products
    Products.__path__.insert(0, products_home)
  else:
    products_home = os.path.join(instance_home, 'Products')

  import OFS.Application
  import_products = OFS.Application.import_products
  from Testing import ZopeTestCase # This will import custom_zodb.py
  OFS.Application.import_products = import_products

  try:
    # On Zope 2.8, ZopeTestCase does not have any logging facility.
    # So we must emulate the usual Zope startup code to catch log
    # messages.
    from ZConfig.matcher import SectionValue
    from ZConfig.components.logger.handlers import FileHandlerFactory
    from ZConfig.components.logger.logger import EventLogFactory
    import logging
    section = SectionValue({'dateformat': '%Y-%m-%d %H:%M:%S',
                            'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
                            'level': logging.INFO,
                            'path': os.environ['EVENT_LOG_FILE']},
                           None, None)
    section.handlers = [FileHandlerFactory(section)]
    eventlog = EventLogFactory(section)
    logger = logging.getLogger()
    logger.handlers = []
    eventlog()
  except ImportError:
    pass
  
  TestRunner = unittest.TextTestRunner
  suite = unittest.TestSuite()

  # allow unit tests of our Products or business templates to be reached.
  from glob import glob
  product_test_list = glob(os.path.join(products_home, '*', 'tests'))
  sys.path.extend(product_test_list)
  bt5_path = os.environ.get('erp5_tests_bt5_path',
                            os.path.join(instance_home, 'bt5'))
  bt5_test_list = glob(os.path.join(bt5_path, '*', 'TestTemplateItem'))
  sys.path.extend(bt5_test_list)
  # also suport instance_home/bt5/project_bt5/*
  project_bt5_test_list = glob(os.path.join(bt5_path, '*', '*', 'TestTemplateItem'))
  sys.path.extend(project_bt5_test_list)

  sys.path.extend((real_tests_home, tests_home))

  # Make sure that locally overridden python modules are used
  sys.path.insert(0, os.path.join(real_instance_home, 'lib', 'python'))

  # XXX Allowing to load modules from here is a wrong idea. use the above path
  # instead.
  # Add tests_framework_home as first path element.
  # this allows to bypass psyco by creating a dummy psyco module
  # it is then possible to run the debugger by "import pdb; pdb.set_trace()"
  sys.path.insert(0, tests_framework_home)

  test_loader = ERP5TypeTestLoader()

  save = int(os.environ.get('erp5_save_data_fs', 0))
  dummy_test = save and (int(os.environ.get('update_business_templates', 0))
                         or not int(os.environ.get('erp5_load_data_fs', 0)))
  if dummy_test:
    # Skip all tests in save mode and monkeypatch PortalTestCase.setUp
    # to skip beforeSetUp and afterSetUp. Also patch unittest.makeSuite,
    # as it's used in test_suite function in test cases.
    from Products.ERP5Type.tests.ERP5TypeTestCase import \
                  dummy_makeSuite, dummy_setUp, dummy_tearDown
    from Testing.ZopeTestCase.PortalTestCase import PortalTestCase
    unittest.makeSuite = dummy_makeSuite
    PortalTestCase.setUp = dummy_setUp
    PortalTestCase.tearDown = dummy_tearDown
    test_loader.testMethodPrefix = 'dummy_test'

  suite = test_loader.loadTestsFromNames(test_list)

  # Hack the profiler to run only specified test methods, and wrap results when
  # running in debug mode. We also monkeypatch unittest.TestCase for tests that
  # does not use ERP5TypeTestCase
  if not dummy_test:
    test_method_list = os.environ.get('run_only', '').split(',')

    def wrapped_run(run_orig):
      # wrap the method that run the test to run test method only if its name
      # matches the run_only spec and to provide post mortem debugging facility
      def run(self, result=None):
        if debug and result:
          result = DebugTestResult(result)
        if not test_method_list:
          return run_orig(self, result)
        test_method_name = self.id().rsplit('.', 1)[-1]
        for valid_test_method_name_re in test_method_list:
          if re.search(valid_test_method_name_re, test_method_name):
            return run_orig(self, result)
      return run

    from Testing.ZopeTestCase import profiler
    profiler.Profiled.__call__ = wrapped_run(profiler.Profiled.__call__)
    from unittest import TestCase
    TestCase.__call__ = wrapped_run(TestCase.__call__)

  # change current directory to the test home, to create zLOG.log in this dir.
  os.chdir(tests_home)
  result = TestRunner(verbosity=verbosity).run(suite)

  if save:
    from Products.ERP5Type.tests.utils import getMySQLArguments
    # The output of mysqldump needs to merge many lines at a time
    # for performance reasons (merging lines is at most 10 times
    # faster, so this produce somewhat not nice to read sql
    command = 'mysqldump %s > %s' % (getMySQLArguments(),
                                     os.path.join(instance_home, 'dump.sql'))
    if verbosity:
      print('Dumping MySQL database with %s... ' % command)
    os.system(command)
    if verbosity:
      print('Dumping static files... ')
    for static_dir in 'Constraint', 'Document', 'Extensions', 'PropertySheet':
      static_dir = os.path.join(instance_home, static_dir)
      try:
        shutil.rmtree(static_dir + '.bak')
      except OSError, e:
        if e.errno != errno.ENOENT:
          raise
      shutil.copytree(static_dir, static_dir + '.bak', symlinks=True)

  return result


def usage(stream, msg=None):
  if msg:
    print >>stream, msg
    print >>stream
  program = os.path.basename(sys.argv[0])
  print >>stream, __doc__ % {"program": program}

def main():
  try:
    opts, args = getopt.getopt(sys.argv[1:],
        "hpvD", ["help", "verbose", "profile", "portal_id=", "data_fs_path=",
        "bt5_path=",
        "recreate_catalog=", "erp5_sql_connection_string=",
        "cmf_activity_sql_connection_string=",
        "erp5_sql_deferred_connection_string=",
        "erp5_catalog_storage=",
        "save",
        "load",
        "email_from_address=",
        "run_only=",
        "update_only=",
        "update_business_templates"] )
  except getopt.GetoptError, msg:
    usage(sys.stderr, msg)
    sys.exit(2)
  
  if WIN:
    os.environ["erp5_tests_bt5_path"] = os.path.join(real_instance_home, 'bt5')

  os.environ["erp5_tests_recreate_catalog"] = "0"
  verbosity = 1
  debug = 0

  for opt, arg in opts:
    if opt in ("-v", "--verbose"):
      os.environ['VERBOSE'] = "1"
      verbosity = 2
    elif opt in ("-h", "--help"):
      usage(sys.stdout)
      sys.exit()
    elif opt == '-D':
      debug = 1
    elif opt in ("-p", "--profile"):
      os.environ['PROFILE_TESTS'] = "1"
      # profiling of setup and teardown is disabled by default, just set
      # environment variables yourself if you want to enable them, but keep in
      # mind that the first time, setup will create a site and install business
      # templates, and this be profiled as well.
      #os.environ['PROFILE_SETUP'] = "1"
      #os.environ['PROFILE_TEARDOWN'] = "1"
    elif opt == '--portal_id':
      os.environ["erp5_tests_portal_id"] = arg
    elif opt == '--data_fs_path':
      os.environ["erp5_tests_data_fs_path"] = arg
      os.environ["erp5_tests_recreate_catalog"] = "1"
    elif opt ==  '--bt5_path':
      os.environ["erp5_tests_bt5_path"] = arg
    elif opt == '--recreate_catalog':
      os.environ["erp5_tests_recreate_catalog"] = arg
    elif opt == "--erp5_sql_connection_string":
      os.environ["erp5_sql_connection_string"] = arg
    elif opt == "--cmf_activity_sql_connection_string":
      os.environ["cmf_activity_sql_connection_string"] = arg
    elif opt == "--erp5_sql_deferred_connection_string":
      os.environ["erp5_sql_deferred_connection_string"] = arg
    elif opt == "--email_from_address":
      os.environ["email_from_address"] = arg
    elif opt == "--save":
      os.environ["erp5_save_data_fs"] = "1"
    elif opt == "--load":
      os.environ["erp5_load_data_fs"] = "1"
    elif opt == "--erp5_catalog_storage":
      os.environ["erp5_catalog_storage"] = arg
    elif opt == "--run_only":
      os.environ["run_only"] = arg
    elif opt == "--update_only":
      os.environ["update_only"] = arg
      os.environ["update_business_templates"] = "1"
    elif opt == "--update_business_templates":
      os.environ["update_business_templates"] = "1"

  test_list = args
  if not test_list:
    print "No test to run, exiting immediately."
    sys.exit(1)

  result = runUnitTestList(test_list=test_list,
                           verbosity=verbosity,
                           debug=debug)
  from Testing.ZopeTestCase import profiler
  profiler.print_stats()
  sys.exit(len(result.failures) + len(result.errors))

if __name__ == '__main__':
  # Force stdout to be totally unbuffered.
  try:
    sys.stdout = os.fdopen(1, "wb", 0)
  except OSError:
    pass

  main()
