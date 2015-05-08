#!/usr/bin/env python2.7
import os
import sys
import pdb
import re
import time
import getopt
import unittest
import signal
import shutil
import errno
import random
import transaction
from glob import glob
try:
  from coverage import coverage
except ImportError:
  coverage = None

WIN = os.name == 'nt'

__doc__ = """%(program)s: unit test runner for the ERP5 Project

usage: %(program)s [options] [UnitTest1[.TestClass1[.testMethod]] [...]]

Options:
  -v, --verbose              produce verbose output
  -h, --help                 this help screen
  -p, --profile              print profiling results at the end
  --coverage=STRING          Use the given path as a coverage config file and
                             thus enable code coverateg report
  --portal_id=STRING         force id of the portal. Useful when using
                             --data_fs_path to run tests on an existing
                             Data.fs
  --data_fs_path=STRING      Use the given path for the Data.fs
  --live_instance=[STRING]   Use Data.fs, Document, PropertySheet, Constraint
                             from a live instance. This is very useful in order
                             to try quickly a test without having to rebuild
                             testing data. This could be totally unsafe for your
                             instance, this depends if the test destroy existing
                             data or not.
                             STRING could be used to define the path of real
                             instance. It automatically enables:
                               --save --load --dump_sql=0 --data_fs_path=...
  --bt5_path                 Search for Business Templates in the given list of
                             paths (or any HTTP url supported by template tool),
                             delimited with commas. In particular, BT can be
                             downloaded directly from a running ERP5 instance
                             using a url like:
                               http://.../erp5/portal_templates/asRepository
                             Default is INSTANCE_HOME/bt5 and its subfolders.
  --recreate_catalog={0|1}   Recreate the content of the SQL catalog. Default
                             is to recreate, unless using --data_fs_path
  --save                     Run unit tests in persistent mode (if unset,
                             existing Data.fs, dump.sql and *.bak static
                             folders are not modified). Tests are skipped
                             if business templates are updated
                             or if --load is unset.
  --load                     Reuse existing instance (created with --save).
  --dump_sql=[0|1]           Force enabling/disabling SQL dumps.
                             By default, databases are loaded/saved except
                             when running ZEO clients.
  --erp5_sql_connection_string=STRING
                             ZSQL Connection string for erp5_sql_connection, by
                             default, it will use "test test"
  --cmf_activity_sql_connection_string=STRING
                             ZSQL Connection string for
                             cmf_activity_sql_connection (if unset, defaults to
                             erp5_sql_connection_string)
  --extra_sql_connection_string_list=STRING
                             Used when 2 or more ZSQL connection strings are
                             needed. By defaut, it will take the last four
                             connection string already existing and created in runTestSuite
  --email_from_address=STRING
                             Initialise the email_from_address property of the
                             portal, by default, CMFActivity failures are sent
                             on localhost from this address, to this address
  --erp5_catalog_storage=STRING
                             Use the given business template as erp5_catalog
                             dependency provider (ie, the name of the BT
                             containing ZSQLMethods matching the desired
                             catalog storage).
  --run_only=STRING          Run only specified test methods delimited with
                             commas (e.g. testFoo,testBar). This can be regular
                             expressions.
  -D                         Invoke debugger on errors / failures.
  --update_business_templates
                             Update all business templates prior to runing
                             tests. This only has a meaning when doing
                             upgratability checks, in conjunction with --load.
                             --update_only can be use to restrict the list of
                             templates to update.
  --update_only=STRING       Specify the list of business template to update if
                             you don't want to update them all. You can give a list
                             delimited with commas (e.g. erp5_core,erp5_xhtml_style).
                             This can be regular expressions.
  --enable_full_indexing=STRING
                             By default, unit test do not reindex everything
                             for performance reasons. Provide list of documents
                             (delimited with comas) for which we want to force
                             indexing. This can only be for now 'portal_types'
  --conversion_server_hostname=STRING
                             Hostname used to connect to conversion server (Oood),
                             this value will stored at default preference.
                             By default localhost is used.
  --conversion_server_port=STRING
                             Port number used to connect to conversion server
                             (Oood), the value will be stored at default preference.
                             By default 8008 is used.
  --volatile_memcached_server_hostname=STRING
                             Hostname used to connect to volatile memcached server,
                             this value will stored on portal_memcached.
                             By default localhost is used.
  --volatile_memcached_server_port=STRING
                             Port number used to connect to volatile memcached server,
                             the value will be stored on portal_memcached.
                             By default 11211 is used.
  --persistent_memcached_server_hostname=STRING
                             Hostname used to connect to persistent memcached server,
                             this value will stored on portal_memcached.
                             By default localhost is used.
  --persistent_memcached_server_port=STRING
                             Port number used to connect to persistent memcached server,
                             the value will be stored on portal_memcached.
                             By default 12121 is used.
  --random_activity_priority=[SEED]
                             Force activities to have a random priority, to make
                             random failures (due to bad activity dependencies)
                             almost always reproducible. A random number
                             generator with the specified seed (or a random one
                             otherwise) is created for this purpose.
  --activity_node=NUMBER     Create given number of ZEO clients, to process
                             activities.
  --zeo_server=[[HOST:]PORT] Bind the ZEO server to the given host/port.
  --zeo_client=[HOST:]PORT   Use specified ZEO server as storage.
  --zserver=[HOST:]PORT[,...]
                             Make ZServer listen on given host:port
                             If used with --activity_node=, this can be a
                             comma-separated list of addresses.
  --neo_storage              Use a NEO storage (SQLite) instead of FileStorage.
  --products_path=path,path  Comma-separated list of products paths locations
                             which shall be used in test environment.
  --sys_path=path,path       Comma-separated list of paths which will be used to
                             extend sys.path
  --instance_home=PATH       Create/use test instance in given path

When no unit test is specified, only activities are processed.
"""

# This script is usually executed directly, and is also imported using its full
# doted name from other locations, such as custom_zodb.py . To prevent
# reloading this module in such case, we store it in sys.modules under that
# name.
sys.modules['Products.ERP5Type.tests.runUnitTest'] = sys.modules[__name__]


def initializeInstanceHome(tests_framework_home,
                           real_instance_home,
                           instance_home):
  assert (os.path.isabs(tests_framework_home)
      and os.path.isabs(real_instance_home)
      and os.path.isabs(instance_home))
  os.path.exists(instance_home) or os.mkdir(instance_home)
  if not WIN:
    # Try to use relative symlinks
    if tests_framework_home.startswith(os.path.join(real_instance_home,
                                                    'Products', '')):
      tests_framework_home = tests_framework_home[len(real_instance_home)+1:]
    if real_instance_home == os.path.dirname(instance_home):
      real_instance_home = 'real_instance'
      d = os.path.join(instance_home, real_instance_home)
      os.path.exists(d) or os.symlink('..', d)
  old_pwd = os.getcwd()
  try:
    os.chdir(instance_home)
    for d in ('bin', 'etc', 'tests', 'var', 'log'):
      if not os.path.exists(d):
        os.mkdir(d)
    for d in ('Products', 'bt5', 'svn', 'lib', 'import'):
      if not os.path.exists(d):
        src = os.path.join(real_instance_home, d)
        if os.path.islink(d):
          os.remove(d)
        if WIN:
          if d in ('Products', 'bt5', 'svn'):
            os.mkdir(d)
          else:
            shutil.copytree(src, d)
        else:
          os.symlink(src, d)
    d = 'custom_zodb.py'
    if not os.path.exists(d):
      src = os.path.join(tests_framework_home, d)
      if os.path.islink(d):
        os.remove(d)
      if WIN:
        shutil.copy(src, d)
      else:
        os.symlink(src, d)
  finally:
    os.chdir(old_pwd)

# site specific variables
tests_framework_home = os.path.dirname(os.path.abspath(__file__))

# find zope home, either from SOFTWARE_HOME environment variable, or by
# guessing some common paths.
if 'SOFTWARE_HOME' in os.environ:
  software_home = os.environ['SOFTWARE_HOME']
  if not os.path.exists(software_home):
    raise ValueError('SOFTWARE_HOME is set to non existing directory %r'
                      % (software_home,))
else:
  common_paths = [
    '/usr/lib/erp5/lib/python',
    '/usr/lib64/zope/lib/python',
    '/usr/lib/zope/lib/python',
  ]
  if WIN:
    erp5_home = os.path.sep.join(tests_framework_home.split(os.path.sep)[:-4])
    common_paths = [os.path.join(erp5_home, 'Zope', 'lib', 'python')]
  # maybe SOFTWARE_HOME is already in sys.path
  try:
    import Zope2
  except ImportError:
    for software_home in common_paths:
      if os.path.isdir(software_home):
        break
    else:
      raise
  else:
    software_home = os.path.dirname(os.path.dirname(Zope2.__file__))
  os.environ['SOFTWARE_HOME'] = software_home

# software_home is zope_home/lib/python, remove lib/python
zope_home = os.path.dirname(os.path.dirname(software_home))

# SOFTWARE_HOME must be early in sys.path, otherwise some products will
# import ImageFile from PIL instead of from Zope!
if software_home not in sys.path:
  sys.path.insert(0, software_home)

# handle 'system global' instance and windows
if WIN:
  real_instance_home = os.path.join(erp5_home, 'ERP5Instance')
elif tests_framework_home.startswith('/usr/lib'):
  real_instance_home = '/var/lib/erp5'
  if not os.path.isdir(real_instance_home):
    real_instance_home = '/var/lib/zope'
elif 'REAL_INSTANCE_HOME' in os.environ:
  real_instance_home = os.path.abspath(os.environ['REAL_INSTANCE_HOME'])
else:
  real_instance_home = os.path.sep.join(
      tests_framework_home.split(os.path.sep)[:-3])

class ERP5TypeTestLoader(unittest.TestLoader):
  """Load test cases from the name passed on the command line.
  """
  filter_test_list = None
  _testMethodPrefix = 'test'

  testMethodPrefix = property(
    lambda self: self._testMethodPrefix,
    lambda self, value: None)

  def loadTestsFromName(self, name, module=None):
    """
    This method is here for compatibility with old style arguments:
    - It is possible to have the .py prefix for the test file

    And, also to load ZODB Test Component before passing it to unittest
    TestLoader().
    """
    # backward compatibility
    if name.endswith('.py'):
      name = name[:-3]

    if ':' in name:
      from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
      from Products.ERP5Type.tests.ERP5TypeLiveTestCase import ERP5TypeLiveTestCase

      class ComponentTestCase(ERP5TypeLiveTestCase):

        def setUp(self):
          super(ComponentTestCase, self).setUp()
          self._callSetUpOnce()

      # Bootstrap has been done in loadTestsFromNames, so the test can now
      # be loaded like any Live Test on a real instance
      if ComponentTestCase not in ERP5TypeTestCase.__bases__:
        ERP5TypeTestCase.__bases__ = ComponentTestCase,

      # TestLoader() does not perform any import so import the Module manually
      module = __import__('erp5.component.test',
                          fromlist=['erp5.component.test'],
                          level=0)

      # TODO-arnau: What about loading a test for a specific Component Version?
      name = name.split(':')[1]

      __import__('erp5.component.test.%s' % name.split('.')[0],
                 ['erp5.component.test'],
                 level=0)

    return super(ERP5TypeTestLoader, self).loadTestsFromName(name, module)

  def loadTestsFromModule(self, module):
    """ERP5Type test loader supports a function named 'test_suite'
    """
    if hasattr(module, 'test_suite'):
      return self.suiteClass(module.test_suite())
    return super(ERP5TypeTestLoader, self).loadTestsFromModule(module)

  def loadTestsFromNames(self, test_list):
    # ZODB Test Components requires bootstrap to install BTs before running the
    # actual test
    test_list_len = len(test_list)
    if test_list_len > 0 and ':' in test_list[0]:
      # TODO-arnau: Does anyone specifies multiple test file on command line, at
      # least test bot does not...
      if test_list_len > 1:
        raise NotImplementedError("Cannot specify multiple Unit Tests to run "
                                  "with ZODB Test Components")

      # Cannot be imported at top-level as importing ERP5TypeTestCase has side
      # effects and a lot of magic has to be done before. Otherwise,
      # getLogger('CMFActivity') was failing because no handlers were set up.
      from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeCommandLineTestCase

      class _ZodbTestComponentBootstrapOnly(ERP5TypeCommandLineTestCase):
        """
        Bootstrap class for ZODB Test Components which reuses as much as possible
        code with "normal" tests as the only difference is how Business Templates are
        installed.

        With legacy tests, a test is directly loaded from the filesystem by adding BTs
        TestTemplateItem directories to sys.path and the list of Business Templates is
        given by its getBusinessTemplateList() method.

        However, with ZODB Components, importing erp5.component.* modules and using
        Component Versions require ERP5 site to be loaded and dependencies BTs to be
        installed beforehand (and the entry point is thus the BT title and the test to
        be loaded as specified on the command line (BT:TEST_NAME instead of
        TEST_NAME)). Any other way would be adhoc and would meant having a different
        behavior between running an Unit Test and a Live Test.
        """
        def __init__(self, test_list):
          self._test_list = test_list
          self._bt_already_installed_list = []

        def getBusinessTemplateList(self):
          """
          Only return the Business Template specifies on the command line, its
          dependencies will be resolved through bt5list and Template Tool
          (dependency_list and test_dependency_list BT properties)
          """
          return [ test.split(':')[0] for test in self._test_list ]

        @staticmethod
        def _getBTPathAndIdList(bt_list):
          """
          Overriden as the original method manually checks BT URLs, handled through
          Template Tool resolveBusinessTemplateList() methods for ZODB Components
          """
          return bt_list

        def _installBusinessTemplateList(self,
                                         bt_list,
                                         update_repository_bt_list=True,
                                         *args,
                                         **kwargs):
          """
          Before installing BTs by calling the original method:

          1/ Get filesystem BT repositories and set them to Template Tool
          2/ Update BT repositories
          3/ Resolve dependencies:
             * dependency_list: recursive.
             * test_dependency_list: non-recursive.
          4/ Install BTs as before
          """
          template_tool = self.portal.portal_templates

          from Products.ERP5.ERP5Site import getBootstrapDirectory
          bt5_path_list = [os.environ.get('erp5_tests_bootstrap_path') or
                           getBootstrapDirectory()]

          bt5_path = os.environ.get('erp5_tests_bt5_path')
          if bt5_path:
            bt5_path_list += {re.sub("(\/\*|\*)", '', bt5_path)
                              for bt5_path in bt5_path.split(',')}
          else:
            from App.config import getConfiguration
            instancehome = getConfiguration().instancehome
            bt5_path_list.append(os.path.join(instancehome, 'bt5'))

          valid_bt5_path_list = []
          for bt5_path in bt5_path_list:
            if bt5_path:
              bt5_path = os.path.expanduser(bt5_path)
              if not os.path.exists(bt5_path):
                _print("Ignoring non existant bt5 path %s\n" % bt5_path)
              else:
                valid_bt5_path_list.append(bt5_path)

          template_tool.updateRepositoryBusinessTemplateList(valid_bt5_path_list)

          url_bt_tuple_list = [
            ('%s/%s' % (repository, bt_title), bt_title) for repository, bt_title in
            template_tool.resolveBusinessTemplateListDependency(
              bt_list,
              with_test_dependency_list=True)]

          return super(_ZodbTestComponentBootstrapOnly,
                       self)._installBusinessTemplateList(url_bt_tuple_list,
                                                          *args, **kwargs)

      _ZodbTestComponentBootstrapOnly(test_list).setUp()

    return super(ERP5TypeTestLoader, self).loadTestsFromNames(test_list)

  def getTestCaseNames(self, testCaseClass):
    """Return a sorted sequence of method names found within testCaseClass

    The returned list only contain names matching --run_only
    """
    name_list = super(ERP5TypeTestLoader, self).getTestCaseNames(testCaseClass)
    if ERP5TypeTestLoader.filter_test_list:
      filtered_name_list = []
      for name in name_list:
        for test in ERP5TypeTestLoader.filter_test_list:
          if test(name):
            filtered_name_list.append(name)
            break
      return filtered_name_list
    return name_list

unittest.loader.TestLoader = ERP5TypeTestLoader

class DebugTestResult:
  """Wrap an unittest.TestResult, invoking pdb on errors / failures
  """
  def __init__(self, result):
    self.result = result

  def _start_debugger(self, tb):
    import Lifetime
    if Lifetime._shutdown_phase:
      return
    try:
      # try ipython if available
      import IPython
      try:
        IPython.InteractiveShell()
        p = IPython.core.debugger.Pdb(color_scheme='Linux')
      except AttributeError: # for ipython-0.10 or before
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

_print = sys.stderr.write

def runUnitTestList(test_list, verbosity=1, debug=0, run_only=None):
  if "zeo_client" in os.environ and "zeo_server" in os.environ:
    _print("conflicting options: --zeo_client and --zeo_server")
    sys.exit(1)
  instance_home =  os.environ['INSTANCE_HOME']
  os.environ.setdefault('EVENT_LOG_FILE', os.path.join(tests_home, 'zLOG.log'))
  os.environ.setdefault('EVENT_LOG_SEVERITY', '-300')

  _print("Loading Zope ... \n")
  _start = time.time()

  import Testing
  # the above import changes cfg.testinghome. Reset it to where our
  # custom_zodb.py can be found. This must be done before importing
  # ZopeTestCase below (Leo: I hate import side-effects with a passion).
  import App.config
  cfg = App.config.getConfiguration()
  cfg.testinghome = instance_home
  cfg.instancehome = instance_home
  from Zope2.Startup.datatypes import DBTab
  cfg.dbtab = DBTab({}, {})
  App.config.setConfiguration(cfg)

  if WIN:
    products_home = os.path.join(real_instance_home, 'Products')
    import Products
    Products.__path__.insert(0, products_home)
  else:
    products_home = os.path.join(instance_home, 'Products')

  from Testing.ZopeTestCase import layer, PortalTestCase, ZopeLite
  _apply_patches = layer._deferred_setup.pop(0)[0]
  assert _apply_patches.__name__ == '_apply_patches'

  # Set debug mode after importing ZopeLite that resets it to 0
  cfg.debug_mode = debug

  from ZConfig.components.logger import handlers, logger, loghandler
  import logging
  root_logger = logging.getLogger()
  # On recent Zope, ZopeTestCase does not have any logging facility.
  # So we must emulate the usual Zope startup code to catch log messages.
  from ZConfig.matcher import SectionValue
  section = SectionValue({'dateformat': '%Y-%m-%d %H:%M:%S',
                          'format': '%(asctime)s.%(msecs)03d %(levelname)s %(name)s %(message)s',
                          'level': logging.INFO,
                          'path': os.environ['EVENT_LOG_FILE'],
                          'max_size': None,
                          'old_files': None,
                          'when': None,
                          'interval': None,
                          'formatter': None,
                          },
                         None, None)
  section.handlers = [handlers.FileHandlerFactory(section)]
  root_logger.handlers = []
  logger.EventLogFactory(section)()

  # allow unit tests of our Products or business templates to be reached.
  product_test_list = glob(os.path.join(products_home, '*', 'tests'))
  sys.path.extend(product_test_list)
  erp5_tests_bt5_path = os.environ.get('erp5_tests_bt5_path',
                              os.path.join(instance_home, 'bt5'))
  bt5_path_list = erp5_tests_bt5_path.split(",")
  bt5_test_list = []
  project_bt5_test_list = []
  for bt5_path in bt5_path_list:
    bt5_test_list.extend(glob(os.path.join(bt5_path,'*','TestTemplateItem')))
    bt5_test_list.extend(glob(os.path.join(bt5_path,'*','TestTemplateItem',
                                           'portal_components')))

    # also suport instance_home/bt5/project_bt5/*
    project_bt5_test_list.extend(glob(os.path.join(bt5_path, '*', '*',
                                                   'TestTemplateItem')))
    project_bt5_test_list.extend(glob(os.path.join(bt5_path, '*', '*',
                                                   'TestTemplateItem',
                                                   'portal_components')))

  sys.path.extend(bt5_test_list)
  sys.path.extend(project_bt5_test_list)

  sys.path.extend((os.path.join(real_instance_home, 'tests'), tests_home))
  sys.path.append(instance_home)
  # Make sure that locally overridden python modules are used
  sys.path.insert(0, os.path.join(real_instance_home, 'lib', 'python'))

  # change current directory to the test home, to create zLOG.log in this dir.
  os.chdir(tests_home)

  from Products.ERP5Type.patches import noZopeHelp
  from OFS.Application import AppInitializer
  AppInitializer.install_session_data_manager = lambda self: None

  # import ERP5TypeTestCase before calling layer.ZopeLite.setUp
  # XXX What if the unit test itself uses 'onsetup' ? We should be able to call
  #     remaining 'onsetup' hooks just before executing the test suite.
  from Products.ERP5Type.tests.ERP5TypeTestCase import \
      ProcessingNodeTestCase, ZEOServerTestCase, dummy_setUp, dummy_tearDown

  # Since we're not using the zope.testing testrunner, we need to set up
  # the layer ourselves
  # FIXME: We should start using Zope layers. Our setup will probably
  # be faster and we could drop most of this code we currently maintain
  # ourselves
  layer.ZopeLite.setUp() # this will import custom_zodb.py
  def assertFalse():
    assert False
  layer.onsetup = assertFalse
  ZopeLite._theApp._p_jar.close()
  ZopeLite._theApp = None

  from Products.ERP5Type.tests.utils import DbFactory
  root_db_name, = cfg.dbtab.databases.keys()
  DbFactory(root_db_name).addMountPoint('/')

  TestRunner = unittest.TextTestRunner

  import Lifetime
  from Zope2.custom_zodb import Storage, save_mysql, \
      node_pid_list, neo_cluster, zeo_server_pid
  def shutdown(signum, frame, signum_set=set()):
    Lifetime.shutdown(0)
    signum_set.add(signum)
    if node_pid_list is None and len(signum_set) > 1:
      # in case of ^C, a child should also receive a SIGHUP from the parent,
      # so we merge the first 2 different signals in a single exception
      signum_set.remove(signal.SIGHUP)
    else:
      raise KeyboardInterrupt
  if signal.getsignal(signal.SIGINT) is not signal.SIG_IGN:
    signal.signal(signal.SIGINT, shutdown)
  signal.signal(signal.SIGHUP, shutdown)

  coverage_config = os.environ.get('coverage', None)
  if coverage_config:
    coverage_process = coverage(config_file=coverage_config)
    coverage_process.start()

  try:
    save = int(os.environ.get('erp5_save_data_fs', 0))
    load = int(os.environ.get('erp5_load_data_fs', 0))
    dummy = save and (int(os.environ.get('update_business_templates', 0))
                      or not load)
    if zeo_server_pid == 0:
      suite = ZEOServerTestCase('asyncore_loop')
    elif node_pid_list is None or not test_list:
      suite = ProcessingNodeTestCase('processing_node')
      if not (dummy or load):
        _print('WARNING: either --save or --load should be used because static'
               ' files are only reloaded by the node installing business'
               ' templates.')
    else:
      if dummy:
        # Skip all tests and monkeypatch PortalTestCase to skip
        # afterSetUp/beforeTearDown.
        ERP5TypeTestLoader._testMethodPrefix = 'dummy_test'
        PortalTestCase.setUp = dummy_setUp
        PortalTestCase.tearDown = dummy_tearDown
      elif debug:
        # Hack the profiler to run only specified test methods,
        # and wrap results when running in debug mode.
        class DebugTextTestRunner(TestRunner):
          def _makeResult(self):
            result = super(DebugTextTestRunner, self)._makeResult()
            return DebugTestResult(result)
        TestRunner = DebugTextTestRunner
      loader = ERP5TypeTestLoader()
      if run_only:
        ERP5TypeTestLoader.filter_test_list = [re.compile(x).search
                for x in run_only.split(',')]
      suite = loader.loadTestsFromNames(test_list)

    if node_pid_list is None:
      result = suite()
    else:
      if not test_list:
        root_logger.handlers.append(loghandler.StreamHandler(sys.stderr))
      _print('done (%.3fs)\n' % (time.time() - _start))
      result = TestRunner(verbosity=verbosity).run(suite)
    transaction.commit()
  except:
    import traceback
    print "runUnitTestList Exception : %r" % (traceback.print_exc(),)
    # finally does not expect opened transaction, even in the
    # case of a Ctrl-C.
    transaction.abort()
    raise
  finally:
    ProcessingNodeTestCase.unregisterNode()
    Storage.close()
    if node_pid_list is not None:
      # Wait that child processes exit. Stop ZEO storage (if any) after all
      # other nodes disconnected.
      for pid in node_pid_list:
        os.kill(pid, signal.SIGHUP)
      for pid in node_pid_list:
        os.waitpid(pid, 0)
      if zeo_server_pid:
        os.kill(zeo_server_pid, signal.SIGHUP)
        os.waitpid(zeo_server_pid, 0)
      if neo_cluster:
        neo_cluster.stop()

  if coverage_config:
    coverage_process.stop()
    coverage_process.save()
    coverage_process.html_report()

  if save and save_mysql:
    save_mysql(verbosity)

  return result


def usage(stream, msg=None):
  if msg:
    print >>stream, msg
    print >>stream
  program = os.path.basename(sys.argv[0])
  print >>stream, __doc__ % {"program": program}

def main(argument_list=None):
  if argument_list is None:
    argument_list = []
  # as this method can be used as entry point extend real sys.argv with
  # passed argument list
  old_argv = sys.argv[:]
  sys.argv = [old_argv[0]]
  sys.argv.extend(argument_list)
  sys.argv.extend(old_argv[1:])
  try:
    opts, args = getopt.getopt(sys.argv[1:],
        "hpvD", ["help", "verbose", "profile", "coverage=", "portal_id=",
        "data_fs_path=",
        "bt5_path=",
        "firefox_bin=",
        "xvfb_bin=",
        "recreate_catalog=", "erp5_sql_connection_string=",
        "cmf_activity_sql_connection_string=",
        "extra_sql_connection_string_list=",
        "conversion_server_port=",
        "conversion_server_hostname=",
        "volatile_memcached_server_port=",
        "volatile_memcached_server_hostname=",
        "persistent_memcached_server_port=",
        "persistent_memcached_server_hostname=",
        "erp5_catalog_storage=",
        "save",
        "load",
        "dump_sql=",
        "email_from_address=",
        "enable_full_indexing=",
        "run_only=",
        "update_only=",
        "update_business_templates",
        "random_activity_priority=",
        "activity_node=",
        "live_instance=",
        "zeo_client=",
        "zeo_server=",
        "zserver=",
        "neo_storage",
        "products_path=",
        "sys_path=",
        "instance_home=",
        ])
  except getopt.GetoptError, msg:
    usage(sys.stderr, msg)
    sys.exit(2)

  if WIN:
    os.environ["erp5_tests_bt5_path"] = os.path.join(real_instance_home, 'bt5')

  os.environ["erp5_tests_recreate_catalog"] = "0"
  verbosity = 1
  debug = 0
  run_only = None
  instance_home = os.path.join(real_instance_home, 'unit_test')

  for opt, arg in opts:
    if opt in ("-v", "--verbose"):
      os.environ['VERBOSE'] = "1"
      verbosity = 2
    elif opt in ("-h", "--help"):
      usage(sys.stdout)
      sys.exit()
    elif opt == '-D':
      debug = 1
      os.environ["erp5_debug_mode"] = str(debug)
    elif opt == "--coverage":
      if coverage:
        os.environ['coverage'] = arg
      else:
        _print("WARNING Coverage module not found")
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
      os.environ["erp5_tests_bt5_path"] = ','.join([arg] +
        os.environ.get('erp5_tests_bt5_path', '').split(','))
    elif opt == '--firefox_bin':
      os.environ["firefox_bin"] = arg
    elif opt == '--xvfb_bin':
      os.environ["xvfb_bin"] = arg
    elif opt == '--recreate_catalog':
      os.environ["erp5_tests_recreate_catalog"] = arg
    elif opt == "--erp5_sql_connection_string":
      os.environ["erp5_sql_connection_string"] = arg
    elif opt == "--cmf_activity_sql_connection_string":
      os.environ["cmf_activity_sql_connection_string"] = arg
    elif opt == "--extra_sql_connection_string_list":
      os.environ["extra_sql_connection_string_list"] = arg
    elif opt == "--email_from_address":
      os.environ["email_from_address"] = arg
    elif opt == "--enable_full_indexing":
      # Here we disable optimisations related to indexing
      os.environ["enable_full_indexing"] = arg
    elif opt == "--save":
      os.environ["erp5_save_data_fs"] = "1"
    elif opt == "--load":
      os.environ["erp5_load_data_fs"] = "1"
    elif opt == "--dump_sql":
      os.environ["erp5_dump_sql"] = arg
    elif opt == "--erp5_catalog_storage":
      os.environ["erp5_catalog_storage"] = arg
    elif opt == "--run_only":
      run_only = arg
    elif opt == "--update_only":
      os.environ["update_only"] = arg
      os.environ["update_business_templates"] = "1"
    elif opt == "--update_business_templates":
      os.environ["update_business_templates"] = "1"
    elif opt == "--conversion_server_hostname":
      os.environ["conversion_server_hostname"] = arg
    elif opt == "--conversion_server_port":
      os.environ["conversion_server_port"] = arg
    elif opt == "--volatile_memcached_server_hostname":
      os.environ["volatile_memcached_server_hostname"] = arg
    elif opt == "--volatile_memcached_server_port":
      os.environ["volatile_memcached_server_port"] = arg
    elif opt == "--persistent_memcached_server_hostname":
      os.environ["persistent_memcached_server_hostname"] = arg
    elif opt == "--persistent_memcached_server_port":
      os.environ["persistent_memcached_server_port"] = arg
    elif opt == "--live_instance":
      os.environ["erp5_load_data_fs"] = "1"
      os.environ["erp5_save_data_fs"] = "1"
      os.environ["erp5_dump_sql"] = "0"
      os.environ["erp5_tests_data_fs_path"] = os.path.join(
        arg or real_instance_home, 'var', 'Data.fs')
    elif opt == "--random_activity_priority":
      os.environ["random_activity_priority"] = arg or \
        str(random.randrange(0, 1<<16))
    elif opt == "--activity_node":
      os.environ["activity_node"] = arg
    elif opt == "--zeo_client":
      os.environ["zeo_client"] = arg
    elif opt == "--zeo_server":
      os.environ["zeo_server"] = arg
    elif opt == "--zserver":
      os.environ["zserver"] = arg
    elif opt == "--neo_storage":
      os.environ["neo_storage"] = ""
    elif opt == "--products_path":
      os.environ["PRODUCTS_PATH"] = arg
    elif opt == "--sys_path":
      sys.path.extend(arg.split(','))
    elif opt == "--instance_home":
      instance_home = os.path.abspath(arg)

  global tests_home
  os.environ['INSTANCE_HOME'] = instance_home
  tests_home = os.path.join(instance_home, 'tests')
  initializeInstanceHome(tests_framework_home,
                         real_instance_home,
                         instance_home)

  result = runUnitTestList(test_list=args,
                           verbosity=verbosity,
                           debug=debug,
                           run_only=run_only,
                           )
  return result and not result.wasSuccessful()

if __name__ == '__main__':
  # Force stdout to be totally unbuffered.
  try:
    sys.stdout = os.fdopen(1, "wb", 0)
  except OSError:
    pass
  sys.exit(main())
