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
