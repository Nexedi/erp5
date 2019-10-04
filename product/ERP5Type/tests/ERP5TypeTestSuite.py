import re, imp, sys, os, shlex, shutil, glob, random
from erp5.util.testsuite import TestSuite, SubprocessError

class ERP5TypeTestSuite(TestSuite):

  FTEST_PASS_FAIL_RE = re.compile(
    ".*Functional Tests (?P<total>\d+) Tests, (?P<failures>\d+) " + \
        "Failures(\,\ (?P<expected_failure>\d+) Expected failures|)")

  def setup(self):
    instance_home = self.instance and 'unit_test.%u' % self.instance \
                                   or 'unit_test'
    tests = os.path.join(instance_home, 'tests')
    if os.path.exists(tests):
      shutil.rmtree(instance_home + '.previous', True)
      shutil.move(tests, instance_home + '.previous')

  def run(self, test):
    return self.runUnitTest(test)

  def runUnitTest(self, *args, **kw):
    if self.instance:
      instance_home = 'unit_test.%u' % self.instance
      args = ('--instance_home', instance_home,) + args
      if self.log_directory:
        log_directory = os.path.join(self.log_directory, self.instance)
        os.mkdir(log_directory)
        args = ('--log_directory', log_directory, ) + args

    if self.__dict__.has_key("bt5_path"):
      args = ("--bt5_path=%s" % self.bt5_path,) + args
    instance_number = self.instance or 1
    if self.zserver_address_list:
      args = (
          '--zserver=%s' % self.zserver_address_list[instance_number-1],
          '--zserver_frontend_url=%s' % self.zserver_frontend_url_list[instance_number-1],
          ) + args
    mysql_db_list = self.mysql_db_list[
             (instance_number-1) * self.mysql_db_count:
             (instance_number) * self.mysql_db_count]
    if len(mysql_db_list) > 1:
      args = ('--extra_sql_connection_string_list=%s' % \
              ','.join(mysql_db_list[1:]),) + args
    firefox_bin = getattr(self, "firefox_bin", None)
    xvfb_bin = getattr(self, "xvfb_bin", None)
    if firefox_bin:
      args = ("--firefox_bin=%s" % firefox_bin,) + args
    if xvfb_bin:
      args = ("--xvfb_bin=%s" % xvfb_bin,) + args
    try:
      runUnitTest = os.environ.get('RUN_UNIT_TEST',
                                   'runUnitTest')
      args = tuple(shlex.split(runUnitTest)) \
           + ('--verbose', '--erp5_sql_connection_string=' + mysql_db_list[0]) \
           + args
      status_dict = self.spawn(*args, **kw)
    except SubprocessError, e:
      status_dict = e.status_dict
    test_log = status_dict['stderr']
    search = self.RUN_RE.search(test_log)
    if search:
      groupdict = search.groupdict()
      status_dict.update(duration=float(groupdict['seconds']),
                         test_count=int(groupdict['all_tests']))
    search = self.STATUS_RE.search(test_log)
    if search:
      groupdict = search.groupdict()
      status_dict.update(
        error_count=int(groupdict['errors'] or 0),
        failure_count=int(groupdict['failures'] or 0)
                     +int(groupdict['unexpected_successes'] or 0),
        skip_count=int(groupdict['skips'] or 0)
                  +int(groupdict['expected_failures'] or 0))
    return status_dict

class ProjectTestSuite(ERP5TypeTestSuite):
  """
  Helper code to locate all tests in a path list.

  To use this class, inherit from it and define the following properties:
  _product_list
    List of product names to search tests in.
  _bt_list
    List of bt names to search tests in.
  _search_path_list:
    List of base paths to search for products & bts.
    Defaults to sys.path (upon getTestList execution).
  """
  _product_list = ()
  _bt_list = ()
  _search_path_list = None

  def _searchDirectory(self, path, path_list):
    """
    Returns a iterator over directories matching <path> inside directories
    given in <path list>.
    """
    _path = os.path
    pjoin = _path.join
    isdir = _path.isdir
    return (y for y in (pjoin(x, path) for x in path_list) if isdir(y))

  def getTestList(self):
    _glob = glob.glob
    path = os.path
    pjoin = path.join
    path_list = self._search_path_list or sys.path
    product_test_file_glob = pjoin('tests', 'test*.py')
    bt_test_file_glob = pjoin('TestTemplateItem', 'test*.py')
    test_file_list = []
    extend = test_file_list.extend
    for product_dir in self._searchDirectory('product', path_list):
      for product_id in self._product_list:
        extend(_glob(pjoin(product_dir, product_id, product_test_file_glob)))
    for bt_dir in self._searchDirectory('bt5', path_list):
      for bt_id in self._bt_list:
        extend(_glob(pjoin(bt_dir, bt_id, bt_test_file_glob)))
    return list(frozenset((path.splitext(path.basename(name))[0]
      for name in test_file_list)))

class SavedTestSuite(ERP5TypeTestSuite):
  """
  Helper code to use --save/--load to reduce execution time.

  To use this class, inherit from it and define the following properties:
  _saved_test_id
    Name of the test to use for --save execution.
  """
  _saved_test_id = None

  def __init__(self, *args, **kw):
    # Use same portal id for all tests run by current instance
    # but keep it (per-run) random.
    self._portal_id = 'portal_%i' % (random.randint(0, sys.maxint), )
    super(SavedTestSuite, self).__init__(*args, **kw)

  def __runUnitTest(self, *args, **kw):
    if self.__dict__.has_key("bt5_path"):
      args = ("--bt5_path=%s" % self.bt5_path,) + args
    return super(SavedTestSuite, self).runUnitTest(
      '--portal_id=' + self._portal_id,
      *args, **kw)

  def runUnitTest(self, *args, **kw):
    return self.__runUnitTest(
      '--load',
      *args, **kw)

  def setup(self):
    super(SavedTestSuite, self).setup()
    self.__runUnitTest('--save', self._saved_test_id)

sys.modules['test_suite'] = module = imp.new_module('test_suite')
for var in SubprocessError, TestSuite, ERP5TypeTestSuite, ProjectTestSuite, \
    SavedTestSuite:
  setattr(module, var.__name__, var)
