from __future__ import print_function

import argparse
import re, os, shlex, glob
import sys, threading, subprocess
import traceback
import errno
import pprint
import six
from six.moves import range

from erp5.util import taskdistribution

if six.PY3:
  stdbin = lambda x: x.buffer
else:
  stdbin = lambda x: x

# PY3: use shlex.quote
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
    output = (lambda data: None) if quiet else stdbin(sys.stdout).write
    stdout_thread = threading.Thread(target=readerthread,
                                     args=(p.stdout, output, stdout))
    stdout_thread.setDaemon(True)
    stdout_thread.start()
  if p.stderr:
    stderr = []
    stderr_thread = threading.Thread(target=readerthread,
        args=(p.stderr, stdbin(sys.stderr).write, stderr))
    stderr_thread.setDaemon(True)
    stderr_thread.start()
  if p.stdout:
    stdout_thread.join()
  if p.stderr:
    stderr_thread.join()
  p.wait()
  return (p.stdout and b''.join(stdout),
          p.stderr and b''.join(stderr))

class SubprocessError(EnvironmentError):
  def __init__(self, status_dict):
    self.status_dict = status_dict
  def __getattr__(self, name):
    return self.status_dict[name]
  def __str__(self):
    return 'Error %i' % self.status_code

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
        db = open(self._filename, 'r+')
      except IOError as e:
        if e.errno != errno.ENOENT:
          raise
        db = open(self._filename, 'w+')
      else:
        try:
          self.__dict__.update(eval(db.read()))
        except Exception:
          pass
      self._db = db
      return db
    self._db
    return super(Persistent, self).__getattribute__(attr)

  def sync(self):
    self._db.seek(0)
    db = dict(x for x in six.iteritems(self.__dict__) if x[0][:1] != '_')
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

  RUN_RE = re.compile(
    br'Ran (?P<all_tests>\d+) tests? in (?P<seconds>\d+\.\d+)s',
    re.DOTALL)

  STATUS_RE = re.compile(br"""
    (OK|FAILED)\s+\(
      (failures=(?P<failures>\d+),?\s*)?
      (errors=(?P<errors>\d+),?\s*)?
      (skipped=(?P<skips>\d+),?\s*)?
      (expected\s+failures=(?P<expected_failures>\d+),?\s*)?
      (unexpected\s+successes=(?P<unexpected_successes>\d+),?\s*)?
    \)
    """, re.DOTALL | re.VERBOSE)

  SUB_STATUS_RE = re.compile(
      br"""SUB\s+RESULT:\s+(?P<all_tests>\d+)\s+Tests,\s+
      (?P<failures>\d+)\s+Failures\s*
      \(?
        (skipped=(?P<skips>\d+),?\s*)?
        (expected\s+failures=(?P<expected_failures>\d+),?\s*)?
        (unexpected\s+successes=(?P<unexpected_successes>\d+),?\s*)?
      \)?
      """,
      re.DOTALL | re.VERBOSE)

  mysql_db_count = 1
  allow_restart = False
  realtime_output = True
  try: # PY3
    stdin = subprocess.DEVNULL
  except AttributeError:
    stdin = open(os.devnull, 'rb')

  def __init__(self, max_instance_count, **kw):
    self.__dict__.update(kw)
    self._path_list = ['tests']
    pool = threading.Semaphore(max_instance_count)
    self.acquire = pool.acquire
    self.release = pool.release
    self._instance = threading.local()
    self._pool = [None] if max_instance_count == 1 else \
                 list(range(1, max_instance_count + 1))
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
      try:
        self._instance.id = instance
        if instance not in self._ready:
          self._ready.add(instance)
          self.setup()
        status_dict = self.run(test)
        if on_stop is not None:
          on_stop(status_dict)
        self._pool.append(self.running.pop(test))
      finally:
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
    cwd = kw.pop('cwd', None)
    env = kw and dict(os.environ, **kw) or None
    command = format_command(*args, **kw)
    print('\n$ ' + command)
    sys.stdout.flush()
    try:
      p = subprocess.Popen(args, stdin=self.stdin, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, env=env, cwd=cwd)
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

# (XXX) The code bellow is an generic extension to run a test for any egg. 
#       The code above was moved from ERP5 code base, because it is generic
#       Enough to be used by others.

class EggTestSuite(TestSuite):
  """Run `python setup.py test` in some directories defined by egg_test_path_dict.

  The following arguments are expected by constructor:

  ``egg_test_path_dict`` is a mapping of paths to packages directories keyed by
  package name. The package name is what will be displayed in the test suite.
  It has to be stable for "test result history" to work as expected.

  The python interpreter is ``python_interpreter``
  """
  def run(self, test):
    print(test)
    try:
      status_dict = self.spawn(
          self.python_interpreter, 'setup.py', 'test',
          cwd=self.egg_test_path_dict[test],
          SLAPOS_SHARED_PART_LIST=self.shared_part_list)
    except SubprocessError as e:
      status_dict = e.status_dict
    test_log = status_dict['stderr']
    search = self.RUN_RE.search(test_log)
    if search:
      groupdict = search.groupdict()
      status_dict.update(duration=float(groupdict['seconds']),
                         test_count=int(groupdict['all_tests']))
    search = self.STATUS_RE.search(test_log)
    def updateStatusDictWithGroup(groupdict):
      status_dict.update(error_count=int(groupdict.get('errors') or 0),
                         failure_count=int(groupdict['failures'] or 0)
                                 +int(groupdict['unexpected_successes'] or 0),
                         skip_count=int(groupdict['skips'] or 0)
                                   +int(groupdict['expected_failures'] or 0))
    if search:
      groupdict = search.groupdict()
      updateStatusDictWithGroup(groupdict)
    # In case the test is used to launch another one (like functional test),
    # look for results inside stderr
    sub_search = self.SUB_STATUS_RE.search(status_dict['stdout'])
    if sub_search:
      groupdict = sub_search.groupdict()
      updateStatusDictWithGroup(groupdict)
      status_dict.update(test_count=int(groupdict['all_tests']))
    return status_dict

  def getTestList(self):
    return list(self.egg_test_path_dict)

def runTestSuite():
  parser = argparse.ArgumentParser(description='Run a test suite.')
  parser.add_argument('--test_suite', help='The test suite name')
  parser.add_argument('--test_suite_title', help='The test suite title',
                      default=None)
  parser.add_argument('--test_node_title', help='The test node title',
                      default=None)
  parser.add_argument('--project_title', help='The project title',
                      default=None)
  parser.add_argument('--revision', help='The revision to test',
                      default='dummy_revision')
  parser.add_argument('--node_quantity', help='Number of parallel tests to run',
                      default=1, type=int)
  parser.add_argument('--master_url',
                      help='The Url of Master controling many suites',
                      default=None)
  parser.add_argument('--frontend_url',
                      help='The url of the frontend of this test node',
                      default=None)
  parser.add_argument('--python_interpreter',
                      help='Path to python interpreter used to run the test suite',
                      default='python')
  parser.add_argument('--source_code_path_list',
                      help='Coma separated list of Eggs folders to test',
                      default='.')
  parser.add_argument('--shared_part_list',
                      help='Shared parts for recursive slapos',
                      default='')

  args = parser.parse_args()
  master = taskdistribution.TaskDistributor(args.master_url)
  test_suite_title = args.test_suite_title or args.test_suite
  revision = args.revision

  # Guess test name from path, we support mainly two cases:
  #  /path/to/erp5.util/                  -> we want erp5.util
  #  /path/to/slapos/software/erp5/test/  -> we want erp5
  egg_test_path_dict = {}
  for test_path in args.source_code_path_list.split(','):
    path, test_name = os.path.split(test_path)
    while test_name in ('', 'test'):
      path, test_name = os.path.split(path)
      assert path != os.path.sep
    egg_test_path_dict[test_name] = test_path

  suite = EggTestSuite(1, test_suite=args.test_suite,
                    node_quantity=args.node_quantity,
                    revision=revision,
                    python_interpreter=args.python_interpreter,
                    egg_test_path_dict=egg_test_path_dict,
                    shared_part_list=args.shared_part_list
                    )

  test_result = master.createTestResult(revision, suite.getTestList(),
    args.test_node_title, suite.allow_restart, test_suite_title,
    args.project_title)
  if test_result is not None:
    assert revision == test_result.revision, (revision, test_result.revision)
    while suite.acquire():
      test = test_result.start(list(suite.running))
      if test is not None:
        suite.start(test.name, lambda status_dict, __test=test:
          __test.stop(**status_dict))
      elif not suite.running:
        break

