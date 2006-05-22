##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Yoshinori Okuji <yo@nexedi.com>
#                    Christophe Dumez <christophe@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
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

from Products.CMFCore.utils import UniqueObject
from Products.ERP5Type.Tool.BaseTool import BaseTool
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile
from Products.ERP5Type.Document.Folder import Folder
from Products.ERP5Type import Permissions
from Products.ERP5Subversion import _dtmldir
from Products.ERP5Subversion.SubversionClient import newSubversionClient
import os, re, commands, time, exceptions
from DateTime import DateTime
from cPickle import dumps, loads
from App.config import getConfiguration
from zExceptions import Unauthorized
from OFS.Image import manage_addFile
from cStringIO import StringIO
from tempfile import mktemp
from shutil import copy
from Products.CMFCore.utils import getToolByName
from Products.ERP5.Document.BusinessTemplate import removeAll, TemplateConditionError
from xml.sax.saxutils import escape
from dircache import listdir
from OFS.Traversable import NotFound

try:
  from base64 import b64encode, b64decode
except ImportError:
  from base64 import encodestring as b64encode, decodestring as b64decode
  
# To keep compatibility with python 2.3
try:
  set
except NameError:
  from sets import Set as set
  
class File(object):
  __slots__ = ('status','name')
  # Constructor
  def __init__(self, name, status) :
    self.status = status
    self.name = name
## End of File Class

class Dir(object):
  __slots__ = ('status','name','sub_dirs','sub_files')
  # Constructor
  def __init__(self, name, status) :
    self.status = status
    self.name = name
    self.sub_dirs = [] # list of sub directories
    self.sub_files = [] # list of sub files

  # return a list of sub directories' names
  def getSubDirsNameList(self) :
    return [d.name for d in self.sub_dirs]

  # return directory in subdirs given its name
  def getDirFromName(self, name):
    for d in self.sub_dirs:
      if d.name == name:
        return d
      
  def getObjectFromName(self, name):
    for d in self.sub_dirs:
      if d.name == name:
        return d
    for f in self.sub_files:
      if f.name == name:
        return f
      
  def getContent(self):
    content = self.sub_dirs
    content.extend(self.sub_files)
    return content
## End of Dir Class

class Error(exceptions.EnvironmentError):
    pass

class SubversionPreferencesError(Exception):
  """The base exception class for the Subversion preferences.
  """
  pass
  
class SubversionUnknownBusinessTemplateError(Exception):
  """The base exception class when business template is unknown.
  """
  pass

class SubversionNotAWorkingCopyError(Exception):
  """The base exception class when business template is unknown.
  """
  pass
      
def copytree(src, dst, symlinks=False):
    """Recursively copy a directory tree using copy().

    If exception(s) occur, an Error is raised with a list of reasons.
    dst dir must exist

    If the optional symlinks flag is true, symbolic links in the
    source tree result in symbolic links in the destination tree; if
    it is false, the contents of the files pointed to by symbolic
    links are copied.
    
    Copyright (c) 2001, 2002, 2003, 2004 Python Software Foundation; All Rights Reserved
    """
    names = listdir(src)
    errors = []
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                if not os.path.exists(dstname):
                  os.makedirs(dstname)
                copytree(srcname, dstname, symlinks)
            else:
                copy(srcname, dstname)
        except (IOError, os.error), why:
            errors.append((srcname, dstname, 'Error: ' + str(why.strerror)))
    if errors:
        raise Error, errors
    
def cacheWalk(top, topdown=True, onerror=None):
  """Directory tree generator.

  modification of os.path.walk to use dircache.listdir
  instead of os.path.listdir
  
  Copyright (c) 2001, 2002, 2003, 2004 Python Software Foundation; All Rights Reserved
  """
  try:
      # Note that listdir and error are globals in this module due
      # to earlier import-*.
      names = listdir(top)
  except error, err:
      if onerror is not None:
          onerror(err)
      return

  dirs, nondirs = [], []
  for name in names:
      if os.path.isdir(os.path.join(top, name)):
          dirs.append(name)
      else:
          nondirs.append(name)

  if topdown:
      yield top, dirs, nondirs
  for name in dirs:
      path = os.path.join(top, name)
      if not os.path.islink(path):
          for x in cacheWalk(path, topdown, onerror):
            yield x
  if not topdown:
      yield top, dirs, nondirs

    
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
    color = '#A1559A' #light purple
  elif 'value' in text:
    color = 'purple'
  elif 'key' in text:
    color = '#0C4F0C'#dark green
  else:
    color='blue'
  return "<font color='%s'>%s</font>"%(color,text,)
    
def colorize(text):
  """Return HTML Code with syntax hightlighting
  """
  # Escape xml before adding html tags
  html = escape(text)
  html = html.replace(' ', '&nbsp;&nbsp;')
  html = html.replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;')
  # Colorize comments
  p = re.compile(r'#.*')
  html = p.sub(colorizeTag, html)
  # Colorize tags
  p = re.compile(r'&lt;.*?&gt;')
  html = p.sub(colorizeTag, html)
  # Colorize strings
  p = re.compile(r'\".*?\"')
  html = p.sub(colorizeTag, html)
  html = html.replace(os.linesep, os.linesep+"<br>")
  return html

class DiffFile:
  # Members :
  # - path : path of the modified file
  # - children : sub codes modified
  # - old_revision
  # - new_revision

  def __init__(self, raw_diff):
    if '@@' not in raw_diff:
      self.binary=True
      return
    else:
      self.binary=False
    self.header = raw_diff.split('@@')[0][:-1]
    # Getting file path in header
    self.path = self.header.split('====')[0][:-1].strip()
    # Getting revisions in header
    for line in self.header.split(os.linesep):
      if line.startswith('--- '):
        tmp = re.search('\\([^)]+\\)$', line)
        self.old_revision = tmp.string[tmp.start():tmp.end()][1:-1].strip()
      if line.startswith('+++ '):
        tmp = re.search('\\([^)]+\\)$', line)
        self.new_revision = tmp.string[tmp.start():tmp.end()][1:-1].strip()
    # Splitting the body from the header
    self.body = os.linesep.join(raw_diff.strip().split(os.linesep)[4:])
    # Now splitting modifications
    self.children = []
    first = True
    tmp = []
    for line in self.body.split(os.linesep):
      if line:
        if line.startswith('@@') and not first:
          self.children.append(CodeBlock(os.linesep.join(tmp)))
          tmp = [line,]
        else:
          first = False
          tmp.append(line)
    self.children.append(CodeBlock(os.linesep.join(tmp)))
    
  def toHTML(self):
    # Adding header of the table
    if self.binary:
      return '<b>Folder or binary file or just no changes!</b><br><br><br>'
    
    html = '''
    <table style="text-align: left; width: 100%%;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr height="18px">
      <td style="background-color: grey"><b><center>%s</center></b></td>
      <td style="background-color: black;" width="2"></td>
      <td style="background-color: grey"><b><center>%s</center></b></td>
    </tr>'''%(self.old_revision, self.new_revision)
    header_color = 'grey'
    for child in self.children:
      # Adding line number of the modification
      html += '''<tr height="18px"><td style="background-color: %s">&nbsp;</td><td style="background-color: black;" width="2"></td><td style="background-color: %s">&nbsp;</td></tr>    <tr height="18px">
      <td style="background-color: rgb(68, 132, 255);"><b>Line %s</b></td>
      <td style="background-color: black;" width="2"></td>
      <td style="background-color: rgb(68, 132, 255);"><b>Line %s</b></td>
      </tr>'''%(header_color, header_color, child.old_line, child.new_line)
      header_color = 'white'
      # Adding diff of the modification
      old_code_list = child.getOldCodeList()
      new_code_list = child.getNewCodeList()
      i=0
      for old_line_tuple in old_code_list:
        new_line_tuple = new_code_list[i]
        new_line = new_line_tuple[0] or ' '
        old_line = old_line_tuple[0] or ' '
        i+=1
        html += '''    <tr height="18px">
        <td style="background-color: %s">%s</td>
        <td style="background-color: black;" width="2"></td>
        <td style="background-color: %s">%s</td>
        </tr>'''%(old_line_tuple[1], escape(old_line).replace(' ', '&nbsp;').replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'), new_line_tuple[1], escape(new_line).replace(' ', '&nbsp;').replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'))
    html += '''  </tbody>
</table><br><br>'''
    return html
      

# A code block contains several SubCodeBlocks
class CodeBlock:
  # Members :
  # - old_line : line in old code (before modif)
  # - new line : line in new code (after modif)
  #
  # Methods :
  # - getOldCodeList() : return code before modif
  # - getNewCodeList() : return code after modif
  # Note: the code returned is a list of tuples (code line, background color)

  def __init__(self, raw_diff):
    # Splitting body and header
    self.body = os.linesep.join(raw_diff.split(os.linesep)[1:])
    self.header = raw_diff.split(os.linesep)[0]
    # Getting modifications lines
    tmp = re.search('^@@ -\d+', self.header)
    self.old_line = tmp.string[tmp.start():tmp.end()][4:]
    tmp = re.search('\+\d+', self.header)
    self.new_line = tmp.string[tmp.start():tmp.end()][1:]
    # Splitting modifications in SubCodeBlocks
    in_modif = False
    self.children = []
    tmp=[]
    for line in self.body.split(os.linesep):
      if line:
        if (line.startswith('+') or line.startswith('-')):
          if in_modif:
            tmp.append(line)
          else:
            self.children.append(SubCodeBlock(os.linesep.join(tmp)))
            tmp = [line,]
            in_modif = True
        else:
            if in_modif:
              self.children.append(SubCodeBlock(os.linesep.join(tmp)))
              tmp = [line,]
              in_modif = False
            else:
              tmp.append(line)
    self.children.append(SubCodeBlock(os.linesep.join(tmp)))
    
  # Return code before modification
  def getOldCodeList(self):
    tmp = []
    for child in self.children:
      tmp.extend(child.getOldCodeList())
    return tmp
    
  # Return code after modification
  def getNewCodeList(self):
    tmp = []
    for child in self.children:
      tmp.extend(child.getNewCodeList())
    return tmp
    
# a SubCodeBlock contain 0 or 1 modification (not more)
class SubCodeBlock:
  def __init__(self, code):
    self.body = code
    self.modification = self._getModif()
    self.old_code_length = self._getOldCodeLength()
    self.new_code_length = self._getNewCodeLength()
    # Choosing background color
    if self.modification == 'none':
      self.color = 'white'
    elif self.modification == 'change':
      self.color = 'rgb(253, 228, 6);'#light orange
    elif self.modification == 'deletion':
      self.color = 'rgb(253, 117, 74);'#light red
    else: # addition
      self.color = 'rgb(83, 253, 74);'#light green
    
  def _getModif(self):
    nb_plus = 0
    nb_minus = 0
    for line in self.body.split(os.linesep):
      if line.startswith("-"):
        nb_minus-=1
      elif line.startswith("+"):
        nb_plus+=1
    if (nb_plus==0 and nb_minus==0):
      return 'none'
    if (nb_minus==0):
      return 'addition'
    if (nb_plus==0):
      return 'deletion'
    return 'change'
      
  def _getOldCodeLength(self):
    nb_lines = 0
    for line in self.body.split(os.linesep):
      if not line.startswith("+"):
        nb_lines+=1
    return nb_lines
      
  def _getNewCodeLength(self):
    nb_lines = 0
    for line in self.body.split(os.linesep):
      if not line.startswith("-"):
        nb_lines+=1
    return nb_lines
  
  # Return code before modification
  def getOldCodeList(self):
    if self.modification=='none':
      old_code = [(x, 'white') for x in self.body.split(os.linesep)]
    elif self.modification=='change':
      old_code = [self._getOldCodeList(x) for x in self.body.split(os.linesep) if self._getOldCodeList(x)[0]]
      # we want old_code_list and new_code_list to have the same length
      if(self.old_code_length < self.new_code_length):
        filling = [(None, self.color)]*(self.new_code_length-self.old_code_length)
        old_code.extend(filling)
    else: # deletion or addition
      old_code = [self._getOldCodeList(x) for x in self.body.split(os.linesep)]
    return old_code
  
  def _getOldCodeList(self, line):
    if line.startswith('+'):
      return (None, self.color)
    if line.startswith('-'):
      return (' '+line[1:], self.color)
    return (line, self.color)
  
  # Return code after modification
  def getNewCodeList(self):
    if self.modification=='none':
      new_code = [(x, 'white') for x in self.body.split(os.linesep)]
    elif self.modification=='change':
      new_code = [self._getNewCodeList(x) for x in self.body.split(os.linesep) if self._getNewCodeList(x)[0]]
      # we want old_code_list and new_code_list to have the same length
      if(self.new_code_length < self.old_code_length):
        filling = [(None, self.color)]*(self.old_code_length-self.new_code_length)
        new_code.extend(filling)
    else: # deletion or addition
      new_code = [self._getNewCodeList(x) for x in self.body.split(os.linesep)]
    return new_code
  
  def _getNewCodeList(self, line):
    if line.startswith('-'):
      return (None, self.color)
    if line.startswith('+'):
      return (' '+line[1:], self.color)
    return (line, self.color)
  
class SubversionTool(BaseTool, UniqueObject, Folder):
  """The SubversionTool provides a Subversion interface to ERP5.
  """
  id = 'portal_subversion'
  meta_type = 'ERP5 Subversion Tool'
  portal_type = 'Subversion Tool'
  allowed_types = ()

  login_cookie_name = 'erp5_subversion_login'
  ssl_trust_cookie_name = 'erp5_subversion_ssl_trust'
  
  top_working_path = getConfiguration().instancehome
  
  # Declarative Security
  security = ClassSecurityInfo()

  #
  #   ZMI methods
  #
  manage_options = ( ( { 'label'      : 'Overview'
                        , 'action'     : 'manage_overview'
                        }
                      ,
                      )
                    + Folder.manage_options
                    )

  security.declareProtected( Permissions.ManagePortal, 'manage_overview' )
  manage_overview = DTMLFile( 'explainSubversionTool', _dtmldir )

  # Filter content (ZMI))
  def __init__(self):
      return Folder.__init__(self, SubversionTool.id)

  # Filter content (ZMI))
  def filtered_meta_types(self, user=None):
      # Filters the list of available meta types.
      all = SubversionTool.inheritedAttribute('filtered_meta_types')(self)
      meta_types = []
      for meta_type in self.all_meta_types():
          if meta_type['name'] in self.allowed_types:
              meta_types.append(meta_type)
      return meta_types
    
  # path is the path in svn working copy
  # return edit_path in zodb to edit it
  # return '#' if no zodb path is found
  def editPath(self, bt, path):
    """Return path to edit file
       path can be relative or absolute
    """
    path = self.relativeToAbsolute(path, bt).replace('\\', '/')
    if 'bt' in path.split('/'):
      # not in zodb
      return '#'
    # if file have been deleted then not in zodb
    if not os.path.exists(path):
      return '#'
    svn_path = self.getSubversionPath(bt).replace('\\', '/')
    edit_path = path.replace(svn_path, '').strip()
    if edit_path == '':
      # not in zodb 
      return '#'
    if edit_path[0] == '/':
      edit_path = edit_path[1:]
    edit_path = '/'.join(edit_path.split('/')[1:]).strip()
    if edit_path == '':
      # not in zodb 
      return '#'
    # remove file extension
    edit_path = os.path.splitext(edit_path)[0]
    # Add beginning and end of url
    edit_path = os.path.join(bt.REQUEST["BASE2"], edit_path, 'manage_main')
    return edit_path
    
  def _encodeLogin(self, realm, user, password):
    # Encode login information.
    return b64encode(dumps((realm, user, password)))

  def _decodeLogin(self, login):
    # Decode login information.
    return loads(b64decode(login))
  
  def goToWorkingCopy(self, bt):
      working_path = self.getSubversionPath(bt)
      os.chdir(working_path)
    
  def setLogin(self, realm, user, password):
    """Set login information.
    """
    # Get existing login information. Filter out old information.
    login_list = []
    request = self.REQUEST
    cookie = request.get(self.login_cookie_name)
    if cookie:
      for login in cookie.split(','):
        if self._decodeLogin(login)[0] != realm:
          login_list.append(login)
    # Set the cookie.
    response = request.RESPONSE
    login_list.append(self._encodeLogin(realm, user, password))
    value = ','.join(login_list)
    expires = (DateTime() + 1).toZone('GMT').rfc822()
    request.set(self.login_cookie_name, value)
    response.setCookie(self.login_cookie_name, value, path = '/', expires = expires)

  def _getLogin(self, target_realm):
    request = self.REQUEST
    cookie = request.get(self.login_cookie_name)
    if cookie:
      for login in cookie.split(','):
        realm, user, password = self._decodeLogin(login)
        if target_realm == realm:
          return user, password
    return None, None
      
  def getHeader(self, bt, file):
    file = self.relativeToAbsolute(file, bt)
    header = "<b><a href='BusinessTemplate_viewSvnShowFile?file="+file+"'>" + file + "</a></b>"
    edit_path = self.editPath(bt, file)
    if edit_path != '#':
      header += "&nbsp;&nbsp;<a href='"+self.editPath(bt, file)+"'><img src='imgs/edit.png' border='0'></a>"
    return header

  def _encodeSSLTrust(self, trust_dict, permanent=False):
    # Encode login information.
    key_list = trust_dict.keys()
    key_list.sort()
    trust_item_list = tuple([(key, trust_dict[key]) for key in key_list])
    return b64encode(dumps((trust_item_list, permanent)))

  def _decodeSSLTrust(self, trust):
    # Decode login information.
    trust_item_list, permanent = loads(b64decode(trust))
    return dict(trust_item_list), permanent
  
  def getPreferredUsername(self):
    """return username in preferences if set of the current username
    """
    username = self.getPortalObject().portal_preferences.getPreferredSubversionUserName()
    if username is None or username.strip() == "":
      # not set in preferences, then we get the current username in zope
      username = self.portal_membership.getAuthenticatedMember().getUserName()
    return username
  
  def diffHTML(self, file_path, bt, revision1=None, revision2=None):
    raw_diff = self.diff(file_path, bt, revision1, revision2)
    return DiffFile(raw_diff).toHTML()
  
  # Display a file content in HTML with syntax highlighting
  def fileHTML(self, bt, file_path):
    file_path = self.relativeToAbsolute(file_path, bt)
    file = open(file_path, 'r')
    if os.path.exists(file_path):
      if os.path.isdir(file_path):
        text = "<b>"+file_path+"</b><hr>"
        text += file_path +" is a folder!"
      else:
        head = "<b>"+file_path+"</b>  <a href='"+self.editPath(bt, file_path)+"'><img src='imgs/edit.png' border='0'></a><hr>"
        text = head + colorize(file.read())
    else:
      # see if tmp file is here (svn deleted file)
      if file_path[-1]==os.sep:
        file_path=file_path[:-1]
      filename = file_path.split(os.sep)[-1]
      tmp_path = os.sep.join(file_path.split(os.sep)[:-1])
      tmp_path = os.path.join(tmp_path,'.svn','text-base',filename+'.svn-base')
      if os.path.exists(tmp_path):
        head = "<b>"+tmp_path+"</b> (svn temporary file)<hr>"
        text = head + colorize(file.read())
      else : # does not exist
        text = "<b>"+file_path+"</b><hr>"
        text += file_path +" does not exist!"
    file.close()
    return text
      
  security.declareProtected(Permissions.ManagePortal, 'acceptSSLServer')
  def acceptSSLServer(self, trust_dict, permanent=False):
    """Accept a SSL server.
    """
    # Get existing trust information.
    trust_list = []
    request = self.REQUEST
    cookie = request.get(self.ssl_trust_cookie_name)
    if cookie:
      trust_list.append(cookie)
    # Set the cookie.
    response = request.RESPONSE
    trust_list.append(self._encodeSSLTrust(trust_dict, permanent))
    value = ','.join(trust_list)
    expires = (DateTime() + 1).toZone('GMT').rfc822()
    request.set(self.ssl_trust_cookie_name, value)
    response.setCookie(self.ssl_trust_cookie_name, value, path = '/', expires = expires)
    
  def acceptSSLPerm(self, trust_dict):
    self.acceptSSLServer(self, trust_dict, True)

  def _trustSSLServer(self, target_trust_dict):
    request = self.REQUEST
    cookie = request.get(self.ssl_trust_cookie_name)
    if cookie:
      for trust in cookie.split(','):
        trust_dict, permanent = self._decodeSSLTrust(trust)
        for key in target_trust_dict.keys():
          if target_trust_dict[key] != trust_dict.get(key):
            continue
        else:
          return True, permanent
    return False, False
    
  def _getClient(self, **kw):
    # Get the svn client object.
    return newSubversionClient(self, **kw)
  
  security.declareProtected('Import/Export objects', 'getSubversionPath')
  # with_name : with business template name at the end of the path
  def getSubversionPath(self, bt, with_name=True):
    # return the working copy path corresponding to
    # the given business template browsing
    # working copy list in preferences (looking
    # only at first level of directories)
    wc_list = self.getPortalObject().portal_preferences.getPreferredSubversionWorkingCopyList()
    if not wc_list:
      wc_list = self.getPortalObject().portal_preferences.default_site_preference.getPreferredSubversionWorkingCopyList()
      if not wc_list:
        raise SubversionPreferencesError, 'Please set at least one Subversion Working Copy in preferences first.'
    if len(wc_list) == 0 :
      raise SubversionPreferencesError, 'Please set at least one Subversion Working Copy in preferences first.'
    bt_name = bt.getTitle()
    for wc in wc_list:
      wc = self._getWorkingPath(wc)
      if not os.path.exists(os.path.join(wc, '.svn')):
        raise SubversionNotAWorkingCopyError, "You must check out working copies in this directory: "+wc+" or choose another path in portal preferences."
      if bt_name in listdir(wc) :
        wc_path = os.path.join(wc, bt_name)
        if os.path.isdir(wc_path):
          if with_name:
            return wc_path
          else:
            return os.sep.join(wc_path.split(os.sep)[:-1])
    raise SubversionUnknownBusinessTemplateError, "Could not find '"+bt_name+"' at first level of working copies."
    
  def getTopWorkingPath(self):
    return self.top_working_path

  def _getWorkingPath(self, path):
    #if path[0] != '/':
    #  path = os.path.join(self.top_working_path, path)
    #path = os.path.abspath(path)
    if not path.startswith(self.top_working_path):
      raise Unauthorized, 'unauthorized access to path %s' % path
    return path
    
  security.declareProtected('Import/Export objects', 'update')
  def update(self, bt):
    """Update a working copy.
    """
    path = self._getWorkingPath(self.getSubversionPath(bt))
    client = self._getClient()
    # Revert local changes in working copy first to import a "pure" BT after update
    self.revert(path=path, recurse=True)
    # Update from SVN
    client.update(path)
    # Import in zodb
    return self.importBT(bt)
  
    security.declareProtected('Import/Export objects', 'updatewc')
  def updatewc(self, bt):
    """Update a working copy.
    """
    path = self._getWorkingPath(self.getSubversionPath(bt))
    client = self._getClient()
    # Update from SVN
    client.update(path)

  security.declareProtected('Import/Export objects', 'switch')
  def switch(self, bt, url):
    """switch SVN repository for a working copy.
    """
    path = self._getWorkingPath(self.getSubversionPath(bt))
    client = self._getClient()
    if url[-1] == '/' :
      url = url[:-1]
    # Update from SVN
    client.switch(path=path, url=url)
  
  security.declareProtected('Import/Export objects', 'add')
  # path can be a list or not (relative or absolute)
  def add(self, path, bt=None):
    """Add a file or a directory.
    """
    if bt is not None:
      if isinstance(path, list) :
        path = [self._getWorkingPath(self.relativeToAbsolute(x, bt)) for x in path]
      else:
        path = self._getWorkingPath(self.relativeToAbsolute(path, bt))
    client = self._getClient()
    return client.add(path)

  security.declareProtected('Import/Export objects', 'info')
  def info(self, bt):
    """return info of working copy
    """
    working_copy = self._getWorkingPath(self.getSubversionPath(bt))
    client = self._getClient()
    return client.info(working_copy)
  
  security.declareProtected('Import/Export objects', 'log')
  # path can be absolute or relative
  def log(self, path, bt):
    """return log of a file or dir
    """
    client = self._getClient()
    return client.log(self._getWorkingPath(self.relativeToAbsolute(path, bt)))
  
  security.declareProtected('Import/Export objects', 'cleanup')
  def cleanup(self, bt):
    """remove svn locks in working copy
    """
    working_copy = self._getWorkingPath(self.getSubversionPath(bt))
    client = self._getClient()
    return client.cleanup(working_copy)

  security.declareProtected('Import/Export objects', 'remove')
  # path can be a list or not (relative or absolute)
  def remove(self, path, bt=None):
    """Remove a file or a directory.
    """
    if bt is not None:
      if isinstance(path, list) :
        path = [self._getWorkingPath(self.relativeToAbsolute(x, bt)) for x in path]
      else:
        path = self._getWorkingPath(self.relativeToAbsolute(path, bt))
    client = self._getClient()
    return client.remove(path)

  security.declareProtected('Import/Export objects', 'move')
  def move(self, src, dest):
    """Move/Rename a file or a directory.
    """
    client = self._getClient()
    return client.move(self._getWorkingPath(src), self._getWorkingPath(dest))

  security.declareProtected('Import/Export objects', 'ls')
  # path can be relative or absolute
  def ls(self, path, bt):
    """Display infos about a file.
    """
    client = self._getClient()
    return client.ls(self._getWorkingPath(self.relativeToAbsolute(path, bt)))

  security.declareProtected('Import/Export objects', 'diff')
  # path can be relative or absolute
  def diff(self, path, bt, revision1=None, revision2=None):
    """Make a diff for a file or a directory.
    """
    client = self._getClient()
    return client.diff(self._getWorkingPath(self.relativeToAbsolute(path, bt)), revision1, revision2)
  
  security.declareProtected('Import/Export objects', 'revert')
  # path can be absolute or relative
  def revert(self, path, bt=None, recurse=False):
    """Revert local changes in a file or a directory.
    """
    client = self._getClient()
    if not isinstance(path, list) :
      path = [self._getWorkingPath(self.relativeToAbsolute(path, bt))]
    if bt is not None:
      path = [self._getWorkingPath(self.relativeToAbsolute(x, bt)) for x in path]
    client.revert(path, recurse)

  security.declareProtected('Import/Export objects', 'revertZODB')
  # path can be absolute or relative
  def revertZODB(self, bt, added_files=None, other_files=None, recurse=False):
    """Revert local changes in a file or a directory
       in ZODB and on hard drive
    """
    client = self._getClient()
    object_to_update = {}
    # Transform params to list if they are not already lists
    if not added_files :
      added_files = []
    if not other_files :
      other_files = []
    if not isinstance(added_files, list) :
      added_files=[added_files]
    if not isinstance(other_files, list) :
      other_files=[other_files]
    
    # Reinstall removed or modified files
    for p in other_files :
      path_list = self._getWorkingPath(p).split(os.sep)
      if 'bt' not in path_list:
        if len(path_list) > 2 :
          tmp = os.sep.join(path_list[2:])
          # Remove file extension
          tmp = os.path.splitext(tmp)[0]
          object_to_update[tmp] = 'install'
    path_added_list = []
    # remove added files
    for p in added_files :
      path_list = self._getWorkingPath(p).split(os.sep)
      if 'bt' not in path_list:
        if len(path_list) > 2 :
          tmp = os.sep.join(path_list[2:])
          # Remove file extension
          tmp = os.path.splitext(tmp)[0]
          path_added_list.append(tmp)
    ## hack to remove objects
    # Create a temporary bt with objects to delete
    tmp_bt = getToolByName(bt, 'portal_templates').newContent(portal_type="Business Template")
    tmp_bt.setTemplatePathList(path_added_list)
    tmp_bt.setTitle('tmp_bt_revert')
    # Build bt
    tmp_bt.edit()
    tmp_bt.build()
    # Install then uninstall it to remove objects from ZODB
    tmp_bt.install()
    tmp_bt.uninstall()
    # Remove it from portal template
    bt.portal_templates.manage_delObjects(ids=tmp_bt.getId())
    #revert changes
    added_files.extend(other_files)
    to_revert = [self.relativeToAbsolute(x, bt) for x in added_files]
    if len(to_revert) != 0 :
      client.revert(to_revert, recurse)
      # Partially reinstall installed bt
      installed_bt = bt.portal_templates.getInstalledBusinessTemplate(                                                          bt.getTitle())
      installed_bt.reinstall(object_to_update=object_to_update, force=0)
    
  security.declareProtected('Import/Export objects', 'resolved')
  # path can be absolute or relative
  def resolved(self, path, bt):
    """remove conflicted status
    """
    client = self._getClient()
    if isinstance(path, list) :
      path = [self._getWorkingPath(self.relativeToAbsolute(x, bt)) for x in path]
    else:
      path = self._getWorkingPath(self.relativeToAbsolute(path, bt))
    return client.resolved(path)
    
  security.declareProtected('Import/Export objects', 'export')
  def export(self, src, dest):
    """Export an unversioned copy of the working copy
    """
    client = self._getClient()
    return client.export(src, dest)

  def relativeToAbsolute(self, path, bt) :
    if path[0] == os.sep:
      # already absolute
      return path
    # relative path
    if path.split(os.sep)[0] == bt.getTitle():
      return os.path.join(self.getSubversionPath(bt, False), path)
    else:
      return os.path.join(self.getSubversionPath(bt), path)

  security.declareProtected('Import/Export objects', 'checkin')
  # path can be relative or absolute (can be a list of paths too)
  def checkin(self, path, bt, log_message=None, recurse=True):
    """Commit local changes.
    """
    if isinstance(path, list) :
      path = [self._getWorkingPath(self.relativeToAbsolute(x, bt)) for x in path]
    else:
      path = self._getWorkingPath(self.relativeToAbsolute(path, bt))
    client = self._getClient()
    return client.checkin(path, log_message, recurse)

  security.declareProtected('Import/Export objects', 'getLastChangelog')
  def getLastChangelog(self, bt):
    """Return last changelog of a business template
    """
    bt_path = self._getWorkingPath(self.getSubversionPath(bt))
    changelog_path = bt_path + os.sep + 'bt' + os.sep + 'change_log'
    changelog=""
    if os.path.exists(changelog_path):
      changelog_file = open(changelog_path, 'r')
      changelog_lines = changelog_file.readlines()
      changelog_file.close()
      for line in changelog_lines:
        if line.strip() == '':
          break
        changelog+=line
    return changelog
    

  security.declareProtected('Import/Export objects', 'status')
  def status(self, path, **kw):
    """Get status.
    """
    client = self._getClient()
    return client.status(self._getWorkingPath(path), **kw)
  
  security.declareProtected('Import/Export objects', 'unversionedFiles')
  def unversionedFiles(self, path, **kw):
    """Return unversioned files
    """
    client = self._getClient()
    status_list = client.status(self._getWorkingPath(path), **kw)
    unversioned_list = []
    for statusObj in status_list:
      if str(statusObj.getTextStatus()) == "unversioned":
        my_dict = {}
        my_dict['uid'] = statusObj.getPath()
        unversioned_list.append(my_dict)
    return unversioned_list
      
  security.declareProtected('Import/Export objects', 'conflictedFiles')
  def conflictedFiles(self, path, **kw):
    """Return unversioned files
    """
    client = self._getClient()
    status_list = client.status(self._getWorkingPath(path), **kw)
    conflicted_list = []
    for statusObj in status_list:
      if str(statusObj.getTextStatus()) == "conflicted":
        my_dict = {}
        my_dict['uid'] = statusObj.getPath()
        conflicted_list.append(my_dict)
    return conflicted_list

  security.declareProtected('Import/Export objects', 'removeAllInList')
  def removeAllInList(self, list):
    """Remove all files and folders in list
    """
    for file in list:
      removeAll(file)
    
  def getModifiedTree(self, bt, show_unmodified=False) :
    # Get subversion path without business template name at the end
    bt_path = self._getWorkingPath(self.getSubversionPath(bt, False))
    if bt_path[-1] != '/':
      bt_path += '/'
    # Business template root directory is the root of the tree
    root = Dir(bt.getTitle(), "normal")
    somethingModified = False
    
    # We browse the files returned by svn status
    for status_obj in self.status(os.path.join(bt_path, bt.getTitle())) :
      # can be (normal, added, modified, deleted, conflicted, unversioned)
      status = str(status_obj.getTextStatus())
      if (show_unmodified or status != "normal") and status != "unversioned":
        somethingModified = True
        # Get object path
        full_path = status_obj.getPath()
        relative_path = full_path.replace(bt_path, '')
        filename = os.path.basename(relative_path)

        # Always start from root
        parent = root
        
        # First we add the directories present in the path to the tree
        # if it does not already exist
        for d in relative_path.split(os.sep)[1:-1] :
          if d :
            if d not in parent.getSubDirsNameList() :
              parent.sub_dirs.append(Dir(d, "normal"))
            parent = parent.getDirFromName(d)
        
        # Consider the whole path which can be a folder or a file
        # We add it the to the tree if it does not already exist
        if os.path.isdir(full_path) :
          if filename == parent.name :
            parent.status = status
          elif filename not in parent.getSubDirsNameList() :
            # Add new dir to the tree
            parent.sub_dirs.append(Dir(filename, str(status)))
          else :
            # update msg status
            tmp = parent.getDirFromName(filename)
            tmp.status = str(status)
        else :
          # add new file to the tree
          parent.sub_files.append(File(filename, str(status)))
    return somethingModified and root
  
  def extractBT(self, bt):
    # first update working copy
    #self.updatewc(bt)
    bt.build()
    svn_path = self._getWorkingPath(self.getSubversionPath(bt) + os.sep)
    path = mktemp() + os.sep
    try:
      bt.export(path=path, local=1)
      # svn del deleted files
      self.deleteOldFiles(svn_path, path, bt)
      # add new files and copy
      self.addNewFiles(svn_path, path, bt)
      self.goToWorkingCopy(bt)
    except (pysvn.ClientError, NotFound, AttributeError, AttributeError, Error), error:
      # Clean up
      self.activate().removeAllInList([path,])
      raise error
    # Clean up
    self.activate().removeAllInList([path,])
    
  def importBT(self, bt):
    return bt.download(self._getWorkingPath(self.getSubversionPath(bt)))
    
  # Get a list of files and keep only parents
  # Necessary before recursively commit removals
  def cleanChildrenInList(self, list):
    res = list
    for file in list:
      res = [x for x in res if file == x or file not in x]
    return res

  # return a set with directories present in the directory
  def getSetDirsForDir(self, directory):
    dir_set = set()
    for root, dirs, files in cacheWalk(directory):
      # don't visit SVN directories
      if '.svn' in dirs:
        dirs.remove('.svn')
      # get Directories
      for name in dirs:
        i = root.replace(directory, '').count(os.sep)
        f = os.path.join(root, name)
        dir_set.add((i, f.replace(directory,'')))
    return dir_set
      
  # return a set with files present in the directory
  def getSetFilesForDir(self, directory):
    dir_set = set()
    for root, dirs, files in cacheWalk(directory):
      # don't visit SVN directories
      if '.svn' in dirs:
        dirs.remove('.svn')
      # get Files
      for name in files:
        i = root.replace(directory, '').count(os.sep)
        f = os.path.join(root, name)
        dir_set.add((i, f.replace(directory,'')))
    return dir_set
  
  # return files present in new_dir but not in old_dir
  # return a set of relative paths
  def getNewFiles(self, old_dir, new_dir):
    if old_dir[-1] != os.sep:
      old_dir += os.sep
    if new_dir[-1] != os.sep:
      new_dir += os.sep
    old_set = self.getSetFilesForDir(old_dir)
    new_set = self.getSetFilesForDir(new_dir)
    return new_set.difference(old_set)

  # return dirs present in new_dir but not in old_dir
  # return a set of relative paths
  def getNewDirs(self, old_dir, new_dir):
    if old_dir[-1] != os.sep:
      old_dir += os.sep
    if new_dir[-1] != os.sep:
      new_dir += os.sep
    old_set = self.getSetDirsForDir(old_dir)
    new_set = self.getSetDirsForDir(new_dir)
    return new_set.difference(old_set)
    
  # svn del files that have been removed in new dir
  def deleteOldFiles(self, old_dir, new_dir, bt):
    # detect removed files
    files_set = self.getNewFiles(new_dir, old_dir)
    # detect removed directories
    dirs_set = self.getNewDirs(new_dir, old_dir)
    # svn del
    list = [x for x in files_set]
    list.sort()
    self.remove([os.path.join(old_dir, x[1]) for x in list])
    list = [x for x in dirs_set]
    list.sort()
    self.remove([os.path.join(old_dir, x[1]) for x in list])
  
  # copy files and add new files
  def addNewFiles(self, old_dir, new_dir, bt):
    # detect created files
    files_set = self.getNewFiles(old_dir, new_dir)
    # detect created directories
    dirs_set = self.getNewDirs(old_dir, new_dir)
    # Copy files
    copytree(new_dir, old_dir)
    # svn add
    list = [x for x in dirs_set]
    list.sort()
    self.add([os.path.join(old_dir, x[1]) for x in list])
    list = [x for x in files_set]
    list.sort()
    self.add([os.path.join(old_dir, x[1]) for x in list])
  
  def treeToXML(self, item, bt) :
    output = "<?xml version='1.0' encoding='iso-8859-1'?>"+ os.linesep
    output += "<tree id='0'>" + os.linesep
    output = self._treeToXML(item, output, bt.getTitle(), True)
    output += "</tree>" + os.linesep
    return output
  
  def _treeToXML(self, item, output, relative_path, first) :
    # Choosing a color coresponding to the status
    status = item.status
    if status == 'added' :
      color = 'green'
    elif status == 'modified' or  status == 'replaced' :
      color = 'orange'
    elif status == 'deleted' :
      color = 'red'
    elif status == 'conflicted' :
      color = 'grey'
    else :
      color = 'black'
    if isinstance(item, Dir) :
      if first :
        output += '<item open="1" text="%s" id="%s" aCol="%s" '\
        'im0="folder.png" im1="folder_open.png" '\
        'im2="folder.png">'%(item.name, relative_path, color) + os.linesep
        first = False
      else :
        output += '<item text="%s" id="%s" aCol="%s" im0="folder.png" ' \
        'im1="folder_open.png" im2="folder.png">'%(item.name,
        relative_path, color) + os.linesep
      for it in item.getContent():
        output = self._treeToXML(item.getObjectFromName(it.name), output, os.path.join(relative_path,it.name),first)
      output += '</item>' + os.linesep
    else :
      output += '<item text="%s" id="%s" aCol="%s" im0="document.png"/>'\
                %(item.name, relative_path, color) + os.linesep
    return output
    
InitializeClass(SubversionTool)
