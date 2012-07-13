import re, imp, sys, threading, os, shlex, subprocess, shutil, glob, random
import traceback

# The content of this file might be partially moved to an egg
# in order to allows parallel tests without the code of ERP5

_format_command_search = re.compile("[[\\s $({?*\\`#~';<>&|]").search
_format_command_escape = lambda s: "'%s'" % r"'\''".join(s.split("'"))
def format_command(*args, **kw):
  cmdline = []
  for k, v in sorted(kw.items()):
    if _format_command_search(v):
      v = _format_command_escape(v)
    cmdline.append('%s=%s' % (k, v))
  for v in args:
    if _format_command_search(v):
      v = _format_command_escape(v)
    cmdline.append(v)
  return ' '.join(cmdline)

def subprocess_capture(p, quiet=False):
  def readerthread(input, output, buffer):
    while True:
      data = input.readline()
      if not data:
        break
      output(data)
      buffer.append(data)
  if p.stdout:
    stdout = []
    output = quiet and (lambda data: None) or sys.stdout.write
    stdout_thread = threading.Thread(target=readerthread,
                                     args=(p.stdout, output, stdout))
    stdout_thread.setDaemon(True)
    stdout_thread.start()
  if p.stderr:
    stderr = []
    stderr_thread = threading.Thread(target=readerthread,
                                     args=(p.stderr, sys.stderr.write, stderr))
    stderr_thread.setDaemon(True)
    stderr_thread.start()
  if p.stdout:
    stdout_thread.join()
  if p.stderr:
    stderr_thread.join()
  p.wait()
  return (p.stdout and ''.join(stdout),
          p.stderr and ''.join(stderr))

class Persistent(object):
  """Very simple persistent data storage for optimization purpose

  This tool should become a standalone daemon communicating only with an ERP5
  instance. But for the moment, it only execute 1 test suite and exists,
  and test suite classes may want some information from previous runs.
  """

  def __init__(self, filename):
    self._filename = filename

  def __getattr__(self, attr):
    if attr == '_db':
      try:
        db = file(self._filename, 'r+')
      except IOError, e:
        if e.errno != errno.ENOENT:
          raise
        db = file(self._filename, 'w+')
      else:
        try:
          self.__dict__.update(eval(db.read()))
        except StandardError:
          pass
      self._db = db
      return db
    self._db
    return super(Persistent, self).__getattribute__(attr)

  def sync(self):
    self._db.seek(0)
    db = dict(x for x in self.__dict__.iteritems() if x[0][:1] != '_')
    pprint.pprint(db, self._db)
    self._db.truncate()

class TestSuite(object):
  """
  Subclasses may redefine the following properties:
  mysql_db_count (integer, >=1)
    Maximum number of SQL databases connection strings needed by any tests ran
    in this suite. Tests will get mysql_db_count - 1 connection strings in
    extra_sql_connection_string_list environment variable.
  """

  mysql_db_count = 1
  allow_restart = False
  realtime_output = True
  stdin = file(os.devnull)

  def __init__(self, max_instance_count, **kw):
    self.__dict__.update(kw)
    self._path_list = ['tests']
    pool = threading.Semaphore(max_instance_count)
    self.acquire = pool.acquire
    self.release = pool.release
    self._instance = threading.local()
    self._pool = max_instance_count == 1 and [None] or \
                 range(1, max_instance_count + 1)
    self._ready = set()
    self.running = {}
    if max_instance_count != 1:
      self.realtime_output = False
    elif os.isatty(1):
      self.realtime_output = True
    self.persistent = Persistent('run_test_suite-%s.tmp'
                                 % self.__class__.__name__)

  instance = property(lambda self: self._instance.id)

  def start(self, test, on_stop=None):
    assert test not in self.running
    self.running[test] = instance = self._pool.pop(0)
    def run():
      self._instance.id = instance
      if instance not in self._ready:
        self._ready.add(instance)
        self.setup()
      status_dict = self.run(test)
      if on_stop is not None:
        on_stop(status_dict)
      self._pool.append(self.running.pop(test))
      self.release()
    thread = threading.Thread(target=run)
    thread.setDaemon(True)
    thread.start()

  def update(self):
    self.checkout() # by default, update everything

  def setup(self):
    pass

  def run(self, test):
    raise NotImplementedError

  def getTestList(self):
    raise NotImplementedError

  def spawn(self, *args, **kw):
    quiet = kw.pop('quiet', False)
    env = kw and dict(os.environ, **kw) or None
    command = format_command(*args, **kw)
    print '\n$ ' + command
    sys.stdout.flush()
    try:
      p = subprocess.Popen(args, stdin=self.stdin, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, env=env)
    except Exception:
      # Catch any exception here, to warn user instead of beeing silent,
      # by generating fake error result
      result = dict(status_code=-1,
                    command=command,
                    stderr=traceback.format_exc(),
                    stdout='')
      raise SubprocessError(result)
    if self.realtime_output:
      stdout, stderr = subprocess_capture(p, quiet)
    else:
      stdout, stderr = p.communicate()
      if not quiet:
        sys.stdout.write(stdout)
      sys.stderr.write(stderr)
    result = dict(status_code=p.returncode, command=command,
                  stdout=stdout, stderr=stderr)
    if p.returncode:
      raise SubprocessError(result)
    return result

class ERP5TypeTestSuite(TestSuite):

  RUN_RE = re.compile(
    r'Ran (?P<all_tests>\d+) tests? in (?P<seconds>\d+\.\d+)s',
    re.DOTALL)

  STATUS_RE = re.compile(r"""
    (OK|FAILED)\s+\(
      (failures=(?P<failures>\d+),?\s*)?
      (errors=(?P<errors>\d+),?\s*)?
      (skipped=(?P<skips>\d+),?\s*)?
      (expected\s+failures=(?P<expected_failures>\d+),?\s*)?
      (unexpected\s+successes=(?P<unexpected_successes>\d+),?\s*)?
    \)
    """, re.DOTALL | re.VERBOSE)

  FTEST_PASS_FAIL_RE = re.compile(
    '.*Functional Tests (?P<total>\d+) Tests, (?P<failures>\d+) Failures')

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
      args = ('--instance_home=unit_test.%u' % self.instance,) + args
    instance_number = self.instance or 1
    mysql_db_list = self.mysql_db_list[
             (instance_number-1) * self.mysql_db_count:
             (instance_number) * self.mysql_db_count]
    if len(mysql_db_list) > 1:
      kw['extra_sql_connection_string_list'] = ','.join(mysql_db_list[1:])
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
      status_dict.update(error_count=int(groupdict['errors'] or 0),
                         failure_count=int(groupdict['failures'] or 0),
                         skip_count=int(groupdict['skips'] or 0)
                                   +int(groupdict['expected_failures'] or 0)
                                   +int(groupdict['unexpected_successes'] or 0))
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

class SubprocessError(EnvironmentError):
  def __init__(self, status_dict):
    self.status_dict = status_dict
  def __getattr__(self, name):
    return self.status_dict[name]
  def __str__(self):
    return 'Error %i' % self.status_code

sys.modules['test_suite'] = module = imp.new_module('test_suite')
for var in SubprocessError, TestSuite, ERP5TypeTestSuite, ProjectTestSuite, \
    SavedTestSuite:
  setattr(module, var.__name__, var)
