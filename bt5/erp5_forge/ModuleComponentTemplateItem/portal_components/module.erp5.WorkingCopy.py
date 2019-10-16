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

import errno, json, os, re, shutil
from base64 import b64encode, b64decode
from tempfile import gettempdir
from AccessControl import Unauthorized
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityInfo import ModuleSecurityInfo
from Acquisition import aq_base, Implicit
from App.config import getConfiguration
from DateTime import DateTime
from ZTUtils import make_query
from Products.ERP5.Document.BusinessTemplate import BusinessTemplateFolder
from Products.ERP5Type.Utils import simple_decorator

@simple_decorator
def selfcached(func):
  """Return a function which stores a computed value in an instance
  at the first call.
  """
  key = '_cache_' + str(id(func))
  def decorated(self, *args):
    try:
      cache = getattr(aq_base(self), key)
      return cache[args]
    except AttributeError:
      result = func(self, *args)
      setattr(self, key, {args: result})
    except KeyError:
      cache[args] = result = func(self, *args)
    return result
  return decorated

class NotAWorkingCopyError(Exception): pass
ModuleSecurityInfo(__name__).declarePublic('NotAWorkingCopyError')

class NotVersionedError(Exception): pass
ModuleSecurityInfo(__name__).declarePublic('NotVersionedError')

class BusinessTemplateNotInstalled(Exception): pass
ModuleSecurityInfo(__name__).declarePublic('BusinessTemplateNotInstalled')

class VcsConflictError(Exception): pass
ModuleSecurityInfo(__name__).declarePublic('VcsConflictError')

def issubdir(parent, child):
  return parent == child or child.startswith(parent + os.sep)

ImplicitType = type(Implicit)

class WorkingCopy(Implicit):

  __allow_access_to_unprotected_subobjects__ = 1
  _registry = []
  reference = None

  class __metaclass__(ImplicitType):

    def __init__(cls, name, bases, d): # pylint: disable=no-self-argument,super-init-not-called
      ImplicitType.__init__(cls, name, bases, d) # pylint: disable=non-parent-init-called
      if cls.reference:
        cls._registry.append((cls.reference, cls))

  def __init__(self, path=None, restricted=False):
    if path:
      self.working_copy = self.checkWorkingPath(path, restricted)

  def getWorkingCopyList(self):
    working_copy_list = []
    preferences = self.getPortalObject().portal_preferences
    for path in preferences.getPreferredWorkingCopyList():
      try:
        getVcsTool(vcs=self.reference, path=path)
        working_copy_list.append(path)
      except NotAWorkingCopyError:
        pass
    return working_copy_list

  def createBusinessTemplateWorkingCopy(self):
    """Create the working copy path corresponding to the given business template
    """
    path = os.path.join(self.working_copy, self.aq_parent.getTitle())
    os.mkdir(path)
    self.working_copy = path

  def checkWorkingPath(self, path, restricted):
    # First remove any '..' to prevent escaping.
    # Note that 'normpath' ignore symlinks so it would not do it correctly.
    parts = path.split(os.sep)
    try:
      i = len(parts) - parts[::-1].index(os.pardir)
      parts[:i] = os.path.realpath(os.sep.join(parts[:i])),
      path = os.sep.join(parts)
    except ValueError:
      pass
    # Allow symlinks inside instance home.
    path = os.path.normpath(os.path.expanduser(path))
    real_path = os.path.realpath(path)
    if restricted and not any(
        issubdir(allowed, path) or issubdir(allowed, real_path)
        for allowed in (getConfiguration().instancehome, gettempdir())):
      if 'Developer' not in getSecurityManager().getUser().getRoles():
        raise Unauthorized("Unauthorized access to path %r."
                         " It is NOT in your Zope home instance." % path)
    if os.path.isdir(real_path):
      return real_path
    raise NotAWorkingCopyError(real_path)

  def _getCookie(self, name, default=None):
    try:
      return json.loads(b64decode(self.REQUEST[name]))
    except StandardError:
      return default

  def _setCookie(self, name, value, days=30):
    portal = self.getPortalObject()
    request = portal.REQUEST
    value = b64encode(json.dumps(value))
    request.set(name, value)
    if days:
      expires = (DateTime() + days).toZone('GMT').rfc822()
      request.RESPONSE.setCookie(name, value, path=portal.absolute_url_path(),
                                 expires=expires)

  # path is the path in svn working copy
  # return edit_path in zodb to edit it
  def editPath(self, path, html=False):
    """Return path to edit file
       path can be relative or absolute
    """
    if os.path.isabs(path):
      return '' # should not happen so maybe we should raise
    if path != '.' and os.path.exists(os.path.join(self.working_copy, path)):
      try:
        path = os.path.splitext(path)[0].split(os.sep)
      except ValueError:
        pass
      else:
        if path[0] != 'bt':
          path[0] = portal = self.getPortalObject().absolute_url_path()
          path.append('manage_main')
          path = '/'.join(path)
          if html:
            return '&nbsp;&nbsp;<a href="%s"><img style="border:0" alt="Edit"' \
                   ' src="%s/ERP5VCS_imgs/edit.png" /></a>' % (path, portal)
          return path
    return ''

  def getHeader(self, path):
    real_path = self.working_copy
    if path != '.':
      real_path = os.path.join(real_path, path)
    return '<a style="font-weight: bold"' \
           ' href="BusinessTemplate_viewVcsShowFile?%s">%s</a>%s' \
           % (make_query(file=path), real_path, self.editPath(path, True))

  def getRemoteComment(self):
    return

  def extractBT(self, business_template):
    """Extract business template to local working copy
    """
    if business_template.getBuildingState() == 'draft':
      business_template.edit()
    business_template.build(update_revision=False)
    self._export(business_template)

  def _export(self, business_template):
    bta = BusinessTemplateWorkingCopy(creation=1, path=self.working_copy)
    self.addremove(*bta.export(business_template))

  def showOld(self, path):
    raise NotAWorkingCopyError

  def update(self, keep=False):
    raise NotAWorkingCopyError

  def hasDiff(self, path):
    try:
      hasDiff = aq_base(self).__hasDiff
    except AttributeError:
      template_tool = self.getPortalObject().portal_templates
      if template_tool.getDiffFilterScriptList():
        getFilteredDiff = template_tool.getFilteredDiff
        diff = self.diff
        hasDiff = lambda path: bool(getFilteredDiff(diff(path)))
      else:
        hasDiff = lambda path: True
      self.__hasDiff = hasDiff
    return hasDiff(path)

  def treeToXML(self, item) :
    """ Convert tree in memory to XML
    """
    output = '<?xml version="1.0" encoding="UTF-8"?>\n<tree id="0">\n'
    output = self._treeToXML(item, output)
    return output + '</tree>\n'

  def _treeToXML(self, item, output, relative_path=''):
    """
     Private function to convert recursively tree
     in memory to XML
    """
    # Choosing a color coresponding to the status
    status = item.status
    if status == 'added':
      color = 'green'
    elif status in ('modified', 'replaced'):
      color = 'orange'
    elif status == 'deleted':
      color = 'red'
    elif status == 'conflicted':
      color = 'grey'
    elif status == 'outdated':
      color = 'purple'
    else :
      color = 'black'
    output += '<item text="%s" id="%s" aCol="%s" ' % (
      item.name, relative_path or '.', color)
    if isinstance(item, Dir):
      if not relative_path:
        output += 'open="1" '
      output += 'im0="folder.png" im1="folder_open.png" im2="folder.png">\n'
      for node in item.sub_dirs + item.sub_files:
        output = self._treeToXML(node, output,
            os.path.join(relative_path, node.name))
      output += '</item>' + os.linesep
    else :
      output += 'im0="document.png"/>\n'
    return output

  def fileHTML(self, path):
    """ Display a file content in HTML with syntax highlighting
    """
    real_path = self.working_copy
    if path != '.':
      real_path = os.path.join(real_path, path)
    head = '<span style="font-weight: bold; color: black;">%s</span>' \
           % real_path
    try:
      with open(os.path.join(self.working_copy, path), 'rU') as f:
        text = f.read()
    except IOError, e:
      if e.errno == errno.EISDIR:
        return '%s<hr/>%r is a folder!' % (head, path)
      if e.errno != errno.ENOENT:
        raise
      head += ' (removed)'
      text = self.showOld(path)
    else:
      head += self.editPath(path, True)
    return '%s<hr/><span style="font-family: monospace">%s</span>' \
           % (head, colorize(text))

  def revertZODB(self, added_file_list=(), other_file_list=(), recurse=False):
    """Revert local changes in a file or a directory
       in ZODB and on hard drive
    """
    # Transform params to list if they are not already lists
    if isinstance(added_file_list, basestring):
      added_file_list = added_file_list,
    if isinstance(other_file_list, basestring):
      other_file_list = other_file_list,

    to_revert = list(added_file_list) + list(other_file_list)
    if not to_revert:
      return
    business_template = self.aq_parent
    template_tool = business_template.getParentValue()
    installed_bt = template_tool.getInstalledBusinessTemplate(
      business_template.getTitle())
    if installed_bt is None:
      raise BusinessTemplateNotInstalled("Revert can't work if the business"
        " template is not installed. Please install it first.")

    # Reinstall removed or modified files
    object_to_update = {}
    for path in other_file_list:
      path_list = os.path.splitext(path)[0].split(os.sep)
      if path_list[0] != 'bt' and len(path_list) > 2:
        object_to_update['/'.join(path_list[2:])] = 'install'
    # remove added files
    path_added_list = []
    for path in added_file_list:
      path_list = os.path.splitext(path)[0].split(os.sep)
      if path_list[0] != 'bt' and len(path_list) > 2:
        path_added_list.append('/'.join(path_list[2:]))

    ## hack to remove objects
    if path_added_list:
      # Create a temporary bt with objects to delete
      tmp_bt = template_tool.newContent(portal_type="Business Template",
                                        temp_object=1,
                                        title='tmp_bt_revert',
                                        template_path_list=path_added_list)
      tmp_bt.edit()
      tmp_bt.build(update_revision=False)
      # Install then uninstall it to remove objects from ZODB
      tmp_bt.install()
      tmp_bt.uninstall()

    # revert changes
    #self.revert(to_revert, recurse)
    installed_bt.reinstall(object_to_update=object_to_update, force=0)


def getVcsTool(vcs=None, path=None, restricted=False):
  ## Initialization of WorkingCopy._registry (used to be done in Products.ERP5VCS __init__)
  # Register Subversion before Git
  try:
    from erp5.component.module import Subversion as _
  except ImportError:
    pass
  from erp5.component.module import Git as _

  if vcs:
    for x in WorkingCopy._registry:
      if x[0] == vcs:
        return x[1](path, restricted)
    raise ValueError("Unsupported Version Control System: %s" % vcs)
  elif path:
    for x in WorkingCopy._registry:
      try:
        return x[1](path, restricted)
      except NotAWorkingCopyError:
        pass
    raise NotAWorkingCopyError(path)
  return WorkingCopy()


class BusinessTemplateWorkingCopy(BusinessTemplateFolder):
  # only works for VCS that have a single metadata folder per working copy

  def _writeString(self, obj, path):
    self.file_set.add(path)
    self._makeParent(path)
    path = os.path.join(self.path, path)
    # write file unless unchanged
    file_obj = None
    try:
      try:
        file_obj = open(path, 'r+b')
      except IOError, e:
        if e.errno == errno.EISDIR:
          shutil.rmtree(path, ignore_errors=True)
        elif e.errno != errno.ENOENT:
          raise
        file_obj = open(path, 'wb')
      else:
        old_size = os.fstat(file_obj.fileno()).st_size
        if len(obj) == old_size and obj == file_obj.read():
          return
        file_obj.seek(0)
      file_obj.write(obj)
      file_obj.truncate()
    finally:
      if file_obj is not None:
        file_obj.close()

  def _makeParent(self, path):
    path = os.path.dirname(path)
    if path and path not in self.dir_set:
      self._makeParent(path)
      real_path = os.path.join(self.path, path)
      if not os.path.exists(real_path):
        os.mkdir(real_path)
      self.dir_set.add(path)

  def export(self, business_template):
    self.file_set = set()
    self.dir_set = set()
    # This will call _writeString for every exported object
    business_template.export(bta=self)
    # Remove dangling files/dirs
    removed_set = set()
    prefix_length = len(os.path.join(self.path, ''))
    for dirpath, dirnames, filenames in os.walk(self.path):
      dirpath = dirpath[prefix_length:]
      for i in xrange(len(dirnames) - 1, -1, -1):
        d = dirnames[i]
        if d[0] != '.':
          d = os.path.join(dirpath, d)
          if d in self.dir_set:
            continue
          shutil.rmtree(os.path.join(self.path, d))
          removed_set.add(d)
        del dirnames[i]
      for f in filenames:
        # Ignore hidden files, at least for submodule support.
        #  e.g. `.git` is a file pointing to the directory in its parent repo
        #        <parent_repo>/.git/modules/<submodule>
        #    or `.gitattributes`, etc.
        if f[0] != '.':
          f = os.path.join(dirpath, f)
          if f not in self.file_set:
            os.remove(os.path.join(self.path, f))
            removed_set.add(f)
    return self.file_set, removed_set

class File(object):
  """ Class that represents a file in memory
  """
  __slots__ = ('status', 'name')
  def __init__(self, name, status):
    self.status = status
    self.name = name

class Dir(object):
  """ Class that reprensents a folder in memory
  """
  __slots__ = ('status', 'name', 'sub_dirs', 'sub_files')
  def __init__(self, name, status):
    self.status = status
    self.name = name
    self.sub_dirs = [] # list of sub directories
    self.sub_files = [] # list of sub files

  def __getitem__(self, key):
    for child in self.sub_dirs:
      if child.name == key:
        return child
    for child in self.sub_files:
      if child.name == key:
        return child
    raise KeyError(key)


from xml.sax.saxutils import escape

NBSP = '&nbsp;'
NBSP_TAB = NBSP*8

def colorizeTag(tag):
  "Return html colored item"
  text = tag.group()
  if text.startswith('#') :
    color = 'grey'
  elif text.startswith('\"') :
    color = 'red'
  elif 'string' in text:
    color = 'green'
  elif 'tuple' in text:
    color = 'orange'
  elif 'dictionary' in text:
    color = 'brown'
  elif 'item' in text:
    color = '#a1559a' #light purple
  elif 'value' in text:
    color = 'purple'
  elif 'key' in text:
    color = '#0c4f0c'#dark green
  else:
    color = 'blue'
  return "<span style='font-family: inherit; color: %s'>%s</span>" \
         % (color, text)

def colorize(text):
  """Return HTML Code with syntax hightlighting
  """
  # Escape xml before adding html tags
  html = escape(text)
  html = html.replace(' ', NBSP)
  html = html.replace('\t', NBSP_TAB)
  # Colorize comments
  pattern = re.compile(r'#.*')
  html = pattern.sub(colorizeTag, html)
  # Colorize tags
  pattern = re.compile(r'&lt;.*?&gt;')
  html = pattern.sub(colorizeTag, html)
  # Colorize strings
  pattern = re.compile(r'\".*?\"')
  html = pattern.sub(colorizeTag, html)
  html = html.replace(os.linesep, os.linesep+"<br/>")
  return html
