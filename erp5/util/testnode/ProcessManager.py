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
import re
import subprocess
import threading
import signal
import sys

class SubprocessError(EnvironmentError):
  def __init__(self, status_dict):
    self.status_dict = status_dict
  def __getattr__(self, name):
    return self.status_dict[name]
  def __str__(self):
    return 'Error %i' % self.status_code

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

class ProcessManager(object):

  stdin = file(os.devnull)

  def __init__(self, log, *args, **kw):
    self.log = log
    self.process_pid_set = set()
    signal.signal(signal.SIGTERM, self.sigterm_handler)
    self.under_cancellation = False

  def spawn(self, *args, **kw):
    if self.under_cancellation:
      raise CancellationError("Test Result was cancelled")
    get_output = kw.pop('get_output', True)
    log_prefix = kw.pop('log_prefix', '')
    new_session = kw.pop('new_session', True)
    subprocess_kw = {}
    cwd = kw.pop('cwd', None)
    if cwd:
      subprocess_kw['cwd'] = cwd
    if new_session:
      subprocess_kw['preexec_fn'] = os.setsid
    raise_error_if_fail = kw.pop('raise_error_if_fail', True)
    env = kw and dict(os.environ, **kw) or None
    command = format_command(*args, **kw)
    self.log('subprocess_kw : %r' % (subprocess_kw,))
    self.log('$ ' + command)
    sys.stdout.flush()
    p = subprocess.Popen(args, stdin=self.stdin, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, env=env, **subprocess_kw)
    self.process_pid_set.add(p.pid)
    stdout, stderr = subprocess_capture(p, self.log, log_prefix,
                                        get_output=get_output)
    result = dict(status_code=p.returncode, command=command,
                  stdout=stdout, stderr=stderr)
    self.process_pid_set.discard(p.pid)
    if self.under_cancellation:
      raise CancellationError("Test Result was cancelled")
    if raise_error_if_fail and p.returncode:
      raise SubprocessError(result)
    return result

  def killPreviousRun(self, cancellation=False):
    self.log('ProcessManager killPreviousRun, going to kill %r' % (self.process_pid_set,))
    if cancellation:
      self.under_cancellation = True
    for pgpid in self.process_pid_set:
      try:
        os.kill(pgpid, signal.SIGTERM)
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
