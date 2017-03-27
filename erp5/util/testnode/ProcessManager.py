##############################################################################
#
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
import os
import getpass
import psutil
import re
import subprocess
import threading
import signal
import sys
import time

MAX_TIMEOUT = 3600 * 4

class SubprocessError(EnvironmentError):
  def __init__(self, status_dict):
    self.status_dict = status_dict
  def __getattr__(self, name):
    return self.status_dict[name]
  def __str__(self):
    return 'Error %i' % self.status_code

class TimeoutError(EnvironmentError):
  def __init__(self):
    pass
  def __str__(self):
    return 'Timeout expired. Process killed'

class CancellationError(EnvironmentError):
  pass

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

def subprocess_capture(p, log, log_prefix, get_output=True):
  def readerthread(input, output, buffer):
    while True:
      data = input.readline()
      if not data:
        break
      if get_output:
        buffer.append(data)
      if log_prefix:
        data = "%s : " % log_prefix +  data
      data = data.rstrip('\n')
      output(data)
  if p.stdout:
    stdout = []
    stdout_thread = threading.Thread(target=readerthread,
                                     args=(p.stdout, log, stdout))
    stdout_thread.daemon = True
    stdout_thread.start()
  if p.stderr:
    stderr = []
    stderr_thread = threading.Thread(target=readerthread,
                                     args=(p.stderr, log, stderr))
    stderr_thread.daemon = True
    stderr_thread.start()
  p.wait()
  if p.stdout:
    stdout_thread.join()
  if p.stderr:
    stderr_thread.join()
  return (p.stdout and ''.join(stdout),
          p.stderr and ''.join(stderr))

def killCommand(pid, log):
  """
  To avoid letting orphaned childs, we stop the process and all it's
  child (until childs does not change) and then we brutally kill
  everyone at the same time
  """
  process = psutil.Process(pid)
  new_child_set = set([x.pid for x in process.children(recursive=True)])
  child_set = None
  os.kill(pid, signal.SIGSTOP)
  while new_child_set != child_set:
    child_set = new_child_set
    log("killCommand, new_child_set : %r, child_set: %r" % (
        new_child_set, child_set))
    for child_pid in child_set:
      os.kill(child_pid, signal.SIGSTOP)
    time.sleep(1)
    child_set = new_child_set
    new_child_set = set([x.pid for x in process.children(recursive=True)])
  log("killCommand, finishing, child_set : %r" % (child_set,))
  for child_pid in child_set:
    os.kill(child_pid, signal.SIGKILL)
  os.kill(pid, signal.SIGKILL)

class ProcessManager(object):

  stdin = file(os.devnull)

  def __init__(self, log, *args, **kw):
    self.log = log
    self.process_pid_set = set()
    signal.signal(signal.SIGTERM, self.sigterm_handler)
    self.under_cancellation = False
    self.p = None
    self.result = None
    self.max_timeout = kw.get("max_timeout") or MAX_TIMEOUT
    self.timer_set = set()

  def spawn(self, *args, **kw):
    def timeoutExpired(p, log):
      if p.poll() is None:
        log('PROCESS TOO LONG OR DEAD, GOING TO BE TERMINATED')
        killCommand(p.pid, log)

    if self.under_cancellation:
      raise CancellationError("Test Result was cancelled")
    get_output = kw.pop('get_output', True)
    log_prefix = kw.pop('log_prefix', '')
    new_session = kw.pop('new_session', True)
    log = kw.pop('log', None)
    if log is None:
      log = self.log
    subprocess_kw = {}
    cwd = kw.pop('cwd', None)
    if cwd:
      subprocess_kw['cwd'] = cwd
    if new_session:
      subprocess_kw['preexec_fn'] = os.setsid
    raise_error_if_fail = kw.pop('raise_error_if_fail', True)
    env = kw and dict(os.environ, **kw) or None
    command = format_command(*args, **kw)
    log('subprocess_kw : %r' % (subprocess_kw,))
    log('$ ' + command)
    sys.stdout.flush()
    p = subprocess.Popen(args, stdin=self.stdin, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, env=env, **subprocess_kw)
    self.process_pid_set.add(p.pid)
    timer = threading.Timer(self.max_timeout, timeoutExpired, args=(p, log))
    self.timer_set.add(timer)
    timer.start()
    stdout, stderr = subprocess_capture(p, log, log_prefix,
                                        get_output=get_output)
    timer.cancel()
    self.timer_set.discard(timer)
    result = dict(status_code=p.returncode, command=command,
                  stdout=stdout, stderr=stderr)
    self.process_pid_set.discard(p.pid)
    if self.under_cancellation:
      raise CancellationError("Test Result was cancelled")
    if raise_error_if_fail and p.returncode:
      raise SubprocessError(result)
    return result

  def getSupportedParameterList(self, program_path):
    return re.findall('^  (--\w+)',
      self.spawn(program_path, '--help')['stdout'], re.M)

  def killall(self, name):
    """
    Allow to kill process with given name.
    Will try to kill only process belonging to current user
    """
    user_login = getpass.getuser()
    to_kill_list = []
    for process in psutil.process_iter():
      if process.username() == user_login and process.name() == name:
        self.log('ProcesssManager, killall on %s having pid %s' % (name, process.pid))
        to_kill_list.append(process.pid)
    for pid in to_kill_list:
      killCommand(pid, self.log)

  def killPreviousRun(self, cancellation=False):
    self.log('ProcessManager killPreviousRun, going to kill %r' % (self.process_pid_set,))
    if cancellation:
      self.under_cancellation = True
    for timer in self.timer_set:
      timer.cancel()
    for pgpid in self.process_pid_set:
      try:
        killCommand(pgpid, self.log)
      except:
        pass
    try:
      if os.path.exists(self.supervisord_pid_file):
        supervisor_pid = int(open(self.supervisord_pid_file).read().strip())
        self.log('ProcessManager killPreviousRun, going to kill supervisor with pid %r' % supervisor_pid)
        os.kill(supervisor_pid, signal.SIGTERM)
    except:
      self.log('ProcessManager killPreviousRun, exception when killing supervisor')
      pass
    self.process_pid_set.clear()

  def sigterm_handler(self, signal, frame):
    self.log('SIGTERM_HANDLER')
    sys.exit(1)
