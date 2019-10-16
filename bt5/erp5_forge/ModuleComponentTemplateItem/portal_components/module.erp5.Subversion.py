# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Yoshinori Okuji <yo@nexedi.com>
#                    Christophe Dumez <christophe@nexedi.com>
#               2010 Julien Muchembled <jm@nexedi.com>
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
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import errno, glob, os, re, shutil
from pysvn import ClientError, Revision, opt_revision_kind, svn_err
import threading
from ZTUtils import make_query
from Products.ERP5Type.Message import translateString
from Products.ERP5Type.Utils import simple_decorator
from Products.ERP5.Document.BusinessTemplate import BusinessTemplateFolder
from erp5.component.module.WorkingCopy import \
  WorkingCopy, Dir, File, selfcached, \
  NotAWorkingCopyError, NotVersionedError, VcsConflictError
from erp5.component.module.SubversionClient import newSubversionClient

# XXX Still not thread safe !!! Proper fix is to never use 'os.chdir'
#     Using a RLock is a temporary quick change that only protects against
#     concurrent uses of ERP5 Subversion.
_chdir_lock = threading.RLock()
@simple_decorator
def chdir_working_copy(func):
  def decorator(self, *args, **kw):
    with _chdir_lock:
      cwd = os.getcwd()
      try:
        os.chdir(self.working_copy)
        return func(self, *args, **kw)
      finally:
        os.chdir(cwd)
  return decorator

class Subversion(WorkingCopy):

  reference = 'svn'
  title = 'Subversion'

  _login_cookie_name = 'erp5_subversion_login'
  _ssl_trust_cookie_name = 'erp5_subversion_ssl_trust'

  def __init__(self, *args, **kw):
    WorkingCopy.__init__(self, *args, **kw)
    try:
      path = self.working_copy
    except AttributeError:
      return
    try:
      self.getRevision()
    except (ClientError, KeyError):
      raise NotAWorkingCopyError(path)

  def setLogin(self, realm, user, password):
    """Set login information.
    """
    login_list = [x for x in self._getCookie(self._login_cookie_name, ())
                    if x[0] != realm]
    login_list.append((realm, user, password))
    self._setCookie(self._login_cookie_name, login_list)

  def _getLogin(self, target_realm):
    try:
      for realm, user, password in self._getCookie(self._login_cookie_name, ()):
        if target_realm == realm:
          return user, password
    except ValueError:
      pass
    return None, None

  def acceptSSLServer(self, trust_dict, permanent=True):
    """Accept a SSL server.
    """
    trust_list = self._getCookie(self._ssl_trust_cookie_name, [])
    trust_list.append(trust_dict)
    self._setCookie(self._ssl_trust_cookie_name, trust_list, permanent and 30)

  def _trustSSLServer(self, target_trust_dict):
    return target_trust_dict in self._getCookie(self._ssl_trust_cookie_name, ())

  def getPreferredUsername(self):
    """return username in preferences if set of the current username
    """
    portal = self.getPortalObject()
    username = portal.portal_preferences.getPreferredSubversionUserName()
    if username:
      username = username.strip()
    return (username or
      # not set in preferences, then we get the current user id in zope
      portal.portal_membership.getAuthenticatedMember().getId())

  def _getClient(self, **kw):
    return newSubversionClient(self, **kw)

  def createBusinessTemplateWorkingCopy(self):
    WorkingCopy.createBusinessTemplateWorkingCopy(self)
    self._getClient().add(self.working_copy)

  @chdir_working_copy
  def update(self, keep=False):
    client = self._getClient()
    if not keep:
      self.revert('.', True)
    # removed unversioned files due to former added files that were reverted
    self._clean('.')
    self._getClient().update('.')
    if keep:
      conflicted_list = self.getConflictedFileList()
      bt_revision = os.path.join('bt', 'revision')
      try:
        conflicted_list.remove(bt_revision)
        self.newRevision()
        client.resolved(bt_revision)
      except ValueError:
        pass
      if conflicted_list:
        raise VcsConflictError("The following files conflict (%r),"
                               " please resolve manually." % (conflicted_list,))
    return self.aq_parent.download('.')

  def showOld(self, path):
    try:
      return self._getClient().cat(os.path.join(self.working_copy, path),
                                   Revision(opt_revision_kind.base))
    except ClientError, e:
      if e.args[1][-1][1] in (errno.ENOENT, svn_err.entry_not_found):
        raise NotVersionedError(path)
      raise

  @selfcached
  def info(self):
    """return info of working copy
    """
    return self._getClient().info(self.working_copy)

  def getRemoteUrl(self):
    return self.info()['url']

  def getRemoteComment(self):
    return 'r%s' % self.info()['revision']

  def getRevision(self, dirty=False):
    r = self.info()['commit_revision']
    if dirty and self._getClient().status(self.working_copy, get_all=False):
      return "%s+" % r
    return r

  def export(self, path, url):
    return self._getClient().export(path, url)

  def log(self, path):
    """return log of a file or dir
    """
    return self._getClient().log(os.path.join(self.working_copy, path))

  @chdir_working_copy
  def clean(self):
    self.revert('.', True)
    self._clean('.')

  def _clean(self, path):
    client = self._getClient()
    for status_obj in client.status(path):
      if str(status_obj.getTextStatus()) == 'unversioned':
        path = status_obj.getPath()
        if os.path.isdir(path):
          shutil.rmtree(path)
        else:
          os.remove(path)

  def cleanup(self):
    """remove svn locks in working copy
    """
    return self._getClient().cleanup(self.working_copy)

  @property
  def diff(self):
    diff = self._getClient().diff
    return lambda path, *args, **kw: \
      diff(os.path.join(self.working_copy, path), *args, **kw)

  @chdir_working_copy
  def revert(self, path, recurse=False, exclude_set=()):
    """Revert local changes in a file or a directory.
    """
    client = self._getClient()
    if isinstance(path, basestring):
      path = [path]
    if recurse and exclude_set:
      added_set = set()
      other_list = []
      for path in path:
        for status in client.status(path):
          path = status.getPath()
          if path not in exclude_set:
            status = str(status.getTextStatus())
            if status == 'added':
              added_set.add(path)
            elif status != 'normal':
              other_list.append(path)
      client.revert(other_list, False)
      path = [x for x in added_set if os.path.dirname(x) not in added_set]
    client.revert(path, recurse)

  @chdir_working_copy
  def resolved(self, path_list):
    """remove conflicted status
    """
    resolved = self._getClient().resolved
    for path in path_list:
      resolved(path)

  @chdir_working_copy
  def commit(self, changelog, added=(), modified=(), removed=()):
    """Commit local changes.
    """
    context = self.aq_parent
    # Pysvn wants unicode objects
    if isinstance(changelog, str):
      changelog = changelog.decode('utf8')

    def getRevisionNumber(revision):
      # get the revision number from a revision,
      # with backward compatibility support
      try:
        return revision.getNumber()
      except AttributeError:
        return revision

    # In order not to commit deleted files in a separate commit,
    # we revert unselected files before committing everything recursively.
    selected_set = set(added)
    selected_set.update(modified)
    selected_set.update(removed)
    assert selected_set, "nothing to commit"
    self.revert('.', recurse=True, exclude_set=selected_set)
    revision = self._getClient().checkin('.', changelog, True)
    return context.REQUEST.RESPONSE.redirect('%s/view?%s' % (
      context.absolute_url_path(),
      make_query(portal_status_message=translateString(
        'Files committed successfully in revision ${revision}',
        mapping=dict(revision=getRevisionNumber(revision))))))

  @chdir_working_copy
  def _export(self, business_template):
    bta = BusinessTemplateWorkingCopy(creation=1, client=self._getClient())
    bta.export(business_template)

  @chdir_working_copy
  def getConflictedFileList(self, path='.'):
    return [x.getPath() for x in self._getClient().status(path)
                        if str(x.getTextStatus()) == 'conflicted']

  @chdir_working_copy
  def getModifiedTree(self, show_unmodified=False):
    """ Return tree of files returned by svn status
    """
    # Business template root directory is the root of the tree
    root = Dir(os.path.basename(self.working_copy), "normal")
    something_modified = False
    # We browse the files returned by svn status
    for status_obj in self._getClient().status(path='', update=False):
      # can be (normal, added, modified, deleted, conflicted, unversioned)
      if str(status_obj.getReposTextStatus()) != 'none':
        status = "outdated"
      else:
        status = str(status_obj.getTextStatus())
        if status == "unversioned" or \
          status == "normal" and not show_unmodified:
          continue
      path = status_obj.getPath()
      if path == '.':
        something_modified = True
        root.status = status
      elif status != "modified" or self.hasDiff(path):
        something_modified = True
        # Get object path
        dirname, basename = os.path.split(path)
        # Always start from root
        parent = root
        if dirname:
          # First we add the directories present in the path to the tree
          # if it does not already exist
          for directory in dirname.split(os.sep):
            try:
              parent = parent[directory]
            except KeyError:
              child = Dir(directory, "normal")
              parent.sub_dirs.append(child)
              parent = child
        # Consider the whole path which can be a folder or a file
        # We add it the to the tree if it does not already exist
        if os.path.isdir(path):
          parent.sub_dirs.append(Dir(basename, str(status)))
        else:
          parent.sub_files.append(File(basename, str(status)))
    return something_modified and root


class BusinessTemplateWorkingCopy(BusinessTemplateFolder):

  def __init__(self, client, **kw):
    self.client = client
    BusinessTemplateFolder.__init__(self, **kw)

  def _writeString(self, obj, path):
    self._makeParent(path)
    status = self.versioned_dict.pop(path, None)
    if status is None:
      self.added_set.add(path)
    else:
      status = str(status.getTextStatus())
      if status == 'deleted':
        self.client.revert(path)
        self.svn_file_set.add(path)
      elif status == 'conflicted':
        match = re.compile(re.escape(path) + r'\.(mine|r\d+)$').match
        self.svn_file_set.difference_update(map(match, glob.glob(path + '.?*')))
    # write file unless unchanged
    try:
      if path in self.svn_file_set:
        self.svn_file_set.remove(path)
        file_obj = open(path, 'r+b')
        old_size = os.fstat(file_obj.fileno()).st_size
        if len(obj) == old_size and obj == file_obj.read():
          return
        file_obj.seek(0)
      else:
        file_obj = open(path, 'wb')
      file_obj.write(obj)
      file_obj.truncate()
    finally:
      file_obj.close()

  def _makeParent(self, path):
    path = os.path.dirname(path)
    if path:
      try:
        status = self.versioned_dict[path]
      except KeyError:
        self.added_set.add(path)
      else:
        if status is None:
          return
        if str(status.getTextStatus()) == 'deleted':
          self.client.revert(path)
      self.versioned_dict[path] = None
      self._makeParent(path)
      if path in self.svn_dir_set:
        self.svn_dir_set.remove(path)
      else:
        os.mkdir(path)

  def export(self, business_template):
    # Dicts to track svn status in case it is not consistent with existing
    # files and directories
    self.versioned_dict = {x.getPath(): x for x in self.client.status('.')
      if str(x.getTextStatus()) not in ('ignored', 'unversioned')}
    del self.versioned_dict['.']
    self.versioned_dict[''] = None
    self.added_set = set()

    # Walk current tree
    self.svn_file_set = set()
    self.svn_dir_set = set()
    prefix_length = len(os.path.join('.', ''))
    for dirpath, dirnames, filenames in os.walk('.'):
      dirpath = dirpath[prefix_length:]
      for i in xrange(len(dirnames) - 1, -1, -1):
        d = dirnames[i]
        if d[0] == '.':
          # Ignore hidden directories (in particular '.svn')
          del dirnames[i]
        else:
          self.svn_dir_set.add(os.path.join(dirpath, d))
      for f in filenames:
        self.svn_file_set.add(os.path.join(dirpath, f))

    # This will call _writeString for every exported object
    business_template.export(bta=self)

    # Remove dangling files/dirs (what is in versioned_dict is removed after)
    self.svn_file_set.difference_update(self.versioned_dict)
    self.svn_dir_set.difference_update(self.versioned_dict)
    for x in self.svn_file_set:
      if os.path.dirname(x) not in self.svn_dir_set:
        os.remove(x)
    for x in self.svn_dir_set:
      if os.path.dirname(x) not in self.svn_dir_set:
        shutil.rmtree(x)

    # Remove deleted files/dirs
    self.client.remove([k for k, v in self.versioned_dict.iteritems()
        if v is not None and self.versioned_dict[os.path.dirname(k)] is None])
    # Add new files/dirs
    self.client.add([x for x in self.added_set
        if os.path.dirname(x) not in self.added_set])
