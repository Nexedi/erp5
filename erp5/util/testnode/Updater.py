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
from . import logger
from .ProcessManager import SubprocessError
from .Utils import rmtree
from slapos.util import bytes2str, str2bytes

SVN_UP_REV = re.compile(r'^(?:At|Updated to) revision (\d+).$')
SVN_CHANGED_REV = re.compile(r'^Last Changed Rev.*:\s*(\d+)', re.MULTILINE)


GIT_TYPE = 'git'
SVN_TYPE = 'svn'

class Updater(object):

  _git_cache = {}

  def __init__(self, repository_path, revision=None, git_binary='git',
      branch=None, realtime_output=True, process_manager=None, url=None,
      working_directory=None):
    self.revision = revision
    self._path_list = []
    self.branch = branch
    self.repository_path = repository_path
    self.git_binary = git_binary
    self.realtime_output = realtime_output
    self.process_manager = process_manager
    self.url = url
    self.working_directory = working_directory

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
    for path, _, file_list in os.walk(path):
      for file in file_list:
        if file[-4:] in ('.pyc', '.pyo'):
          # allow several processes clean the same folder at the same time
          try:
            os.remove(os.path.join(path, file))
          except OSError as e:
            if e.errno != errno.ENOENT:
              raise

  def spawn(self, *args, **kw):
    cwd = kw.pop("cwd", None)
    if cwd is None:
      cwd = self.getRepositoryPath()
    return self.process_manager.spawn(*args, 
                                      log_prefix='git',
                                      cwd=cwd,
                                      **kw)

  def _git(self, *args, **kw):
    return bytes2str(self.spawn(self.git_binary, *args, **kw)['stdout'].strip())

  def git_update_server_info(self):
    return self._git('update-server-info', '-f')

  def git_create_repository_link(self):
    """ Create a link in repository to the ".git" directory.
        ex:
        for "../erp5/.git"
        "../erp5/erp5.git"->"../erp5/.git" will be created.
    """
    git_repository_path = os.path.join(self.getRepositoryPath(), '.git')
    name = os.path.basename(os.path.normpath(self.getRepositoryPath()))
    git_repository_link_path = os.path.join(self.getRepositoryPath(), '%s.git' %name)
    logger.debug("checking link %s -> %s..",
             git_repository_link_path, git_repository_path)
    if ( not os.path.lexists(git_repository_link_path) and \
         not os.path.exists(git_repository_link_path) ):
      try:
        os.symlink(git_repository_path, git_repository_link_path)
        logger.debug("link: %s -> %s created",
          git_repository_link_path, git_repository_path)
      except OSError:
        logger.error("Cannot create link from %s -> %s",
          git_repository_link_path, git_repository_path)

  def git_gc_auto(self):
    self._git("gc", "--auto")

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
      h = self._git('log', '-1', '--format=%H', '--full-history', '--', *path_list)
      return self._git_find_rev(h)
    elif self.getRepositoryType() == SVN_TYPE:
      stdout = self.spawn('svn', 'info', *path_list)['stdout']
      return str(max(map(int, SVN_CHANGED_REV.findall(stdout))))
    raise NotImplementedError

  def deleteRepository(self):
    logger.info("Wrong repository or wrong url, deleting repos %s",
             self.repository_path)
    rmtree(self.repository_path)

  def checkRepository(self):
    # make sure that the repository is like we expect
    if self.url:
      if os.path.exists(self.repository_path):
        correct_url = False
        try:
          remote_url = self._git("config", "--get", "remote.origin.url")
          if remote_url == self.url:
            correct_url = True
        except SubprocessError:
          logger.exception("")
        if not(correct_url):
          self.deleteRepository()
      if not os.path.exists(self.repository_path):
        parameter_list = ['clone', self.url]
        if self.branch is not None:
          parameter_list += '-b', self.branch
        parameter_list.append(self.repository_path)
        self._git(*parameter_list, cwd=self.working_directory)
        # Disable automatic GC because we're usually cloned in shared mode.
        # We call 'gc auto' explicitly, when it's safe.
        self._git("config", "gc.auto" , "0")

  def checkout(self, *path_list):
    self.checkRepository()
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
          self._git('clean', '-fdx')
          # For performance, it is ok to use 'git reset --hard',
          # theses days it is not slow like it was long time ago.
          self._git('reset', '--hard', h)
      else:
        self._git('clean', '-fdx')
        if os.path.exists('.git/svn'):
          self._git('svn', 'rebase')
        else:
          self._git('fetch', '--all', '--prune')
          if self.branch and \
            not ("* %s" % self.branch in self._git('branch').split("\n")):
              # Delete branch if already exists
              if self.branch in [x.strip() for x in self._git('branch').split("\n")]:
                self._git('branch', '-D', self.branch)
              self._git('checkout',  'origin/%s' % self.branch, '-b',
                        self.branch)
          self._git('reset', '--hard', '@{u}')
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
        except SubprocessError as e:
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
    self.git_update_server_info()
