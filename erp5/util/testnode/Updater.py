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
import errno
import os
import re
import subprocess
import sys
import threading

from testnode import SubprocessError

SVN_UP_REV = re.compile(r'^(?:At|Updated to) revision (\d+).$')
SVN_CHANGED_REV = re.compile(r'^Last Changed Rev.*:\s*(\d+)', re.MULTILINE)

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

GIT_TYPE = 'git'
SVN_TYPE = 'svn'

class Updater(object):

  _git_cache = {}
  stdin = file(os.devnull)

  def __init__(self, repository_path, log, revision=None, git_binary=None,
      realtime_output=True):
    self.log = log
    self.revision = revision
    self._path_list = []
    self.repository_path = repository_path
    self.git_binary = git_binary
    self.realtime_output = realtime_output

  def getRepositoryPath(self):
    return self.repository_path

  def getRepositoryType(self):
    try:
      return self.repository_type
    except AttributeError:
      # guess the type of repository we have
      if os.path.isdir(os.path.join(
                       self.getRepositoryPath(), '.git')):
        repository_type = GIT_TYPE
      elif os.path.isdir(os.path.join(
                       self.getRepositoryPath(), '.svn')):
        repository_type = SVN_TYPE
      else:
        raise NotImplementedError
      self.repository_type = repository_type
      return repository_type

  def deletePycFiles(self, path):
    """Delete *.pyc files so that deleted/moved files can not be imported"""
    for path, dir_list, file_list in os.walk(path):
      for file in file_list:
        if file[-4:] in ('.pyc', '.pyo'):
          # allow several processes clean the same folder at the same time
          try:
            os.remove(os.path.join(path, file))
          except OSError, e:
            if e.errno != errno.ENOENT:
              raise

  def spawn(self, *args, **kw):
    quiet = kw.pop('quiet', False)
    env = kw and dict(os.environ, **kw) or None
    command = format_command(*args, **kw)
    self.log('$ ' + command)
    sys.stdout.flush()
    p = subprocess.Popen(args, stdin=self.stdin, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, env=env,
                         cwd=self.getRepositoryPath())
    if self.realtime_output:
      stdout, stderr = subprocess_capture(p, quiet)
    else:
      stdout, stderr = p.communicate()
      self.log(stdout)
      self.log(stderr)
    result = dict(status_code=p.returncode, command=command,
                  stdout=stdout, stderr=stderr)
    if p.returncode:
      raise SubprocessError(result)
    return result

  def _git(self, *args, **kw):
    return self.spawn(self.git_binary, *args, **kw)['stdout'].strip()

  def _git_find_rev(self, ref):
    try:
      return self._git_cache[ref]
    except KeyError:
      if os.path.exists('.git/svn'):
        r = self._git('svn', 'find-rev', ref)
        assert r
        self._git_cache[ref[0] != 'r' and 'r%u' % int(r) or r] = ref
      else:
        r = self._git('rev-list', '--topo-order', '--count', ref), ref
      self._git_cache[ref] = r
      return r

  def getRevision(self, *path_list):
    if not path_list:
      path_list = self._path_list
    if self.getRepositoryType() == GIT_TYPE:
      h = self._git('log', '-1', '--format=%H', '--', *path_list)
      return self._git_find_rev(h)
    elif self.getRepositoryType() == SVN_TYPE:
      stdout = self.spawn('svn', 'info', *path_list)['stdout']
      return str(max(map(int, SVN_CHANGED_REV.findall(stdout))))
    raise NotImplementedError

  def checkout(self, *path_list):
    if not path_list:
      path_list = '.',
    revision = self.revision
    if self.getRepositoryType() == GIT_TYPE:
      # edit .git/info/sparse-checkout if you want sparse checkout
      if revision:
        if type(revision) is str:
          h = revision
        else:
          h = revision[1]
        if h != self._git('rev-parse', 'HEAD'):
          self.deletePycFiles('.')
          # For performance reasons, 'reset --merge' only looks at mtime & ctime
          # to check is the index is correct and conflicts immediately if
          # contents or metadata changed. Even hardlinking a file changes its
          # ctime, so at least for buildout (local download), we need to
          # refresh index first.
          self._git('update-index', '--refresh')
          self._git('reset', '--merge', h)
      else:
        self.deletePycFiles('.')
        if os.path.exists('.git/svn'):
          self._git('svn', 'rebase')
        else:
          self._git('fetch')
          self._git('update-index', '--refresh') # see note above
          self._git('reset', '--merge', '@{u}')
        self.revision = self._git_find_rev(self._git('rev-parse', 'HEAD'))
    elif self.getRepositoryType() == SVN_TYPE:
      # following code allows sparse checkout
      def svn_mkdirs(path):
        path = os.path.dirname(path)
        if path and not os.path.isdir(path):
          svn_mkdirs(path)
          self.spawn(*(args + ['--depth=empty', path]))
      for path in path_list:
        args = ['svn', 'up', '--force', '--non-interactive']
        if revision:
          args.append('-r%s' % revision)
        svn_mkdirs(path)
        args += '--set-depth=infinity', path
        self.deletePycFiles(path)
        try:
          status_dict = self.spawn(*args)
        except SubprocessError, e:
          if 'cleanup' not in e.stderr:
            raise
          self.spawn('svn', 'cleanup', path)
          status_dict = self.spawn(*args)
        if not revision:
          self.revision = revision = SVN_UP_REV.findall(
            status_dict['stdout'].splitlines()[-1])[0]
    else:
      raise NotImplementedError
    self._path_list += path_list
