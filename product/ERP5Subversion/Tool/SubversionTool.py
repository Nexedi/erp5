##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Yoshinori Okuji <yo@nexedi.com>
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
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile
from Products.ERP5Type.Document.Folder import Folder
from Products.ERP5Type import Permissions
from Products.ERP5Subversion import _dtmldir
from zLOG import LOG, WARNING, INFO
from Products.ERP5Subversion.SubversionClient import newSubversionClient
import os, re, commands
from DateTime import DateTime
from cPickle import dumps, loads
from App.config import getConfiguration
from zExceptions import Unauthorized
from OFS.Image import manage_addFile
from cStringIO import StringIO

try:
  from base64 import b64encode, b64decode
except ImportError:
  from base64 import encodestring as b64encode, decodestring as b64decode
  
class File :
  # Constructor
  def __init__(self, full_path, msg_status) :
    self.full_path = full_path
    self.msg_status = msg_status
    self.name = full_path.split('/')[-1]
## End of File Class

class Dir :
  # Constructor
  def __init__(self, full_path, msg_status) :
    self.full_path = full_path
    self.msg_status = msg_status
    self.name = full_path.split('/')[-1]
    self.sub_dirs = [] # list of sub directories

  # return a list of sub directories' names
  def getSubDirs(self) :
    return [d.name for d in self.sub_dirs]

  # return directory in subdirs given its name
  def getDir(self, name):
    for d in self.sub_dirs:
      if d.name == name:
        return d
## End of Dir Class

class DiffFile:
  # Members :
  # - path : path of the modified file
  # - children : sub codes modified
  # - old_revision
  # - new_revision

  def __init__(self, raw_diff):
    self.header = raw_diff.split('@@')[0][:-1]
    # Getting file path in header
    self.path = self.header.split('====')[0][:-1].strip()
    # Getting revisions in header
    for line in self.header.split('\n'):
      if line.startswith('--- '):
        tmp = re.search('\\([\w\s]+\\)$', line)
        self.old_revision = tmp.string[tmp.start():tmp.end()][1:-1].strip()
      if line.startswith('+++ '):
        tmp = re.search('\\([\w\s]+\\)$', line)
        self.new_revision = tmp.string[tmp.start():tmp.end()][1:-1].strip()
    # Splitting the body from the header
    self.body = '\n'.join(raw_diff.strip().split('\n')[4:])
    # Now splitting modifications
    self.children = []
    first = True
    tmp = []
    for line in self.body.split('\n'):
      if line:
        if line.startswith('@@') and not first:
          self.children.append(CodeBlock('\n'.join(tmp)))
          tmp = [line,]
        else:
          first = False
          tmp.append(line)
    self.children.append(CodeBlock('\n'.join(tmp)))
    

  def _escape(self, data):
    """
      Escape &, <, and > in a string of data.
      This is a copy of the xml.sax.saxutils.escape function.
    """
    # must do ampersand first
    if data:
      #data = data.replace("&", "&amp;")
      data = data.replace(">", "&gt;")
      data = data.replace("<", "&lt;")
      return data
    
  def toHTML(self):
    # Adding header of the table
    html = '''
    <table style="text-align: left; width: 100%%;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr height="18px">
      <td style="background-color: grey"><b><center>%s</center></b></td>
      <td style="background-color: black;" width="2"></td>
      <td style="background-color: grey"><b><center>%s</center></b></td>
    </tr>'''%(self.old_revision, self.new_revision)
    First = True
    for child in self.children:
      # Adding line number of the modification
      if First:
        html += '''<tr height="18px"><td style="background-color: grey">&nbsp;</td><td style="background-color: black;" width="2"></td><td style="background-color: grey">&nbsp;</td></tr>    <tr height="18px">
        <td style="background-color: rgb(68, 132, 255);"><b>Line %s</b></td>
        <td style="background-color: black;" width="2"></td>
        <td style="background-color: rgb(68, 132, 255);"><b>Line %s</b></td>
      </tr>'''%(child.old_line, child.new_line)
        First = False
      else:
        html += '''<tr height="18px"><td style="background-color: white">&nbsp;</td><td style="background-color: black;" width="2"></td><td style="background-color: white">&nbsp;</td></tr>    <tr height="18px">
        <td style="background-color: rgb(68, 132, 255);"><b>Line %s</b></td>
        <td style="background-color: black;" width="2"></td>
        <td style="background-color: rgb(68, 132, 255);"><b>Line %s</b></td>
      </tr>'''%(child.old_line, child.new_line) 
      # Adding diff of the modification
      old_code_list = child.getOldCodeList()
      new_code_list = child.getNewCodeList()
      i=0
      for old_line_tuple in old_code_list:
        new_line_tuple = new_code_list[i]
        if new_line_tuple[0]:
          new_line = new_line_tuple[0]
        else:
          new_line = ' '
        if old_line_tuple[0]:
          old_line = old_line_tuple[0]
        else:
          old_line = ' '
        i+=1
        html += '''    <tr height="18px">
      <td style="background-color: %s">%s</td>
      <td style="background-color: black;" width="2"></td>
      <td style="background-color: %s">%s</td>
    </tr>'''%(old_line_tuple[1], self._escape(old_line).replace(' ', '&nbsp;').replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'), new_line_tuple[1], self._escape(new_line).replace(' ', '&nbsp;').replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'))
    html += '''  </tbody>
</table></font><br><br>'''
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
    self.body = '\n'.join(raw_diff.split('\n')[1:])
    self.header = raw_diff.split('\n')[0]
    # Getting modifications lines
    tmp = re.search('^@@ -\d+', self.header)
    self.old_line = tmp.string[tmp.start():tmp.end()][4:]
    tmp = re.search('\+\d+,', self.header)
    self.new_line = tmp.string[tmp.start():tmp.end()][1:-1]
    # Splitting modifications in SubCodeBlocks
    in_modif = False
    self.children = []
    tmp=[]
    for line in self.body.split('\n'):
      if line:
        if (line.startswith('+') or line.startswith('-')):
          if in_modif:
            tmp.append(line)
          else:
            self.children.append(SubCodeBlock('\n'.join(tmp)))
            tmp = [line,]
            in_modif = True
        else:
            if in_modif:
              self.children.append(SubCodeBlock('\n'.join(tmp)))
              tmp = [line,]
              in_modif = False
            else:
              tmp.append(line)
    self.children.append(SubCodeBlock('\n'.join(tmp)))
    
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
    else:
      self.color = 'rgb(83, 253, 74);'#light green
    
  def _getModif(self):
    nb_plus = 0
    nb_minus = 0
    for line in self.body.split('\n'):
      if line.startswith("-"):
        nb_minus-=1
      elif line.startswith("+"):
        nb_plus+=1
    if (nb_plus!=0 and nb_minus==0):
      return 'addition'
    if (nb_plus==0 and nb_minus!=0):
      return 'deletion'
    if (nb_plus==0 and nb_minus==0):
      return 'none'
    return 'change'
      
  def _getOldCodeLength(self):
    nb_lines = 0
    for line in self.body.split('\n'):
      if not line.startswith("+"):
        nb_lines+=1
    return nb_lines
      
  def _getNewCodeLength(self):
    nb_lines = 0
    for line in self.body.split('\n'):
      if not line.startswith("-"):
        nb_lines+=1
    return nb_lines
  
  # Return code before modification
  def getOldCodeList(self):
    if self.modification=='none':
      old_code = [(x, 'white') for x in self.body.split('\n')]
    elif self.modification=='change':
      old_code = [self._getOldCodeList(x) for x in self.body.split('\n') if self._getOldCodeList(x)[0]]
      # we want old_code_list and new_code_list to have the same length
      if(self.old_code_length < self.new_code_length):
        filling = [(None, self.color)]*(self.new_code_length-self.old_code_length)
        old_code.extend(filling)
    else: # deletion or addition
      old_code = [self._getOldCodeList(x) for x in self.body.split('\n')]
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
      new_code = [(x, 'white') for x in self.body.split('\n')]
    elif self.modification=='change':
      new_code = [self._getNewCodeList(x) for x in self.body.split('\n') if self._getNewCodeList(x)[0]]
      # we want old_code_list and new_code_list to have the same length
      if(self.new_code_length < self.old_code_length):
        filling = [(None, self.color)]*(self.old_code_length-self.new_code_length)
        new_code.extend(filling)
    else: # deletion or addition
      new_code = [self._getNewCodeList(x) for x in self.body.split('\n')]
    return new_code
  
  def _getNewCodeList(self, line):
    if line.startswith('-'):
      return (None, self.color)
    if line.startswith('+'):
      return (' '+line[1:], self.color)
    return (line, self.color)
  
class SubversionTool(UniqueObject, Folder):
  """The SubversionTool provides a Subversion interface to ERP5.
  """
  id = 'portal_subversion'
  meta_type = 'ERP5 Subversion Tool'
  portal_type = 'Subversion Tool'
  allowed_types = ()

  login_cookie_name = 'erp5_subversion_login'
  ssl_trust_cookie_name = 'erp5_subversion_ssl_trust'
  top_working_path = os.path.join(getConfiguration().instancehome, 'svn')

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

  def getTopWorkingPath(self):
    return self.top_working_path

  def _getWorkingPath(self, path):
    if path[0] != '/':
      path = os.path.join(self.top_working_path, path)
    path = os.path.abspath(path)
    if not path.startswith(self.top_working_path):
      raise Unauthorized, 'unauthorized access to path %s' % path
    return path
    
  def setWorkingDirectory(self, path):
    self.workingDirectory = path
    os.chdir(path)

  def getDefaultUserName(self):
    """Return a default user name.
    """
    name = self.portal_preferences.getPreferredSubversionUserName()
    if not name:
      name = self.portal_membership.getAuthenticatedMember().getUserName()
    return name
    
  def _encodeLogin(self, realm, user, password):
    # Encode login information.
    return b64encode(dumps((realm, user, password)))

  def _decodeLogin(self, login):
    # Decode login information.
    return loads(b64decode(login))
    
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
  
  def diffHTML(self, file_path):
    raw_diff = self.diff(file_path)
    return DiffFile(raw_diff).toHTML()
  
  # Display a file content in HTML
  def fileHTML(self, file_path):
#     file = open(file_path, 'r')
#     text = file.read()
#     file.close()
#     # Escaping
#     text = text.replace("&", "&amp;")
#     text = text.replace(">", "&gt;")
#     text = text.replace("<", "&lt;")
#     # Adding HTML stuff
#     text = text.replace('\n', '<br>')
#     text = text.replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;')
#     text = text.replace('  ', '&nbsp;&nbsp;')
    text = commands.getoutput('enscript -B --color --highlight=html --language=html -o - %s'%file_path)
    text = '\n'.join(text.split('\n')[10:-4])
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

  security.declareProtected('Import/Export objects', 'update')
  def update(self, path):
    """Update a working copy.
    """
    client = self._getClient()
    return client.update(path)

  security.declareProtected('Import/Export objects', 'add')
  def add(self, path):
    """Add a file or a directory.
    """
    client = self._getClient()
    return client.add(path)

  security.declareProtected('Import/Export objects', 'remove')
  def remove(self, path):
    """Remove a file or a directory.
    """
    client = self._getClient()
    return client.remove(path)

  security.declareProtected('Import/Export objects', 'move')
  def move(self, src, dest):
    """Move/Rename a file or a directory.
    """
    client = self._getClient()
    return client.move(src, dest)

  security.declareProtected('Import/Export objects', 'diff')
  def diff(self, path):
    """Make a diff for a file or a directory.
    """
    client = self._getClient()
    return client.diff(path)

  security.declareProtected('Import/Export objects', 'revert')
  def revert(self, path):
    """Revert local changes in a file or a directory.
    """
    client = self._getClient()
    return client.revert(path)

  security.declareProtected('Import/Export objects', 'checkin')
  def checkin(self, path, log_message = 'None', recurse=True):
    """Commit local changes.
    """
    client = self._getClient(login=self.login)
    #return client.checkin(self._getWorkingPath(path), log_message, recurse)
    return client.checkin(path, log_message, recurse)

  security.declareProtected('Import/Export objects', 'status')
  def status(self, path, **kw):
    """Get status.
    """
    client = self._getClient()
    return client.status(path, **kw)
  
  def getModifiedTree(self, path) :
    # Remove trailing slash if it's present
    if path[-1]=="/" :
      path = path[:-1]
    
    root = Dir(path, "normal")
    somethingModified = False
    
    for statusObj in self.status(path) :
      # can be (normal, added, modified, deleted, conflicted, unversioned)
      msg_status = statusObj.getTextStatus()
      if str(msg_status) != "normal" and str(msg_status) != "unversioned":
        somethingModified = True
        full_path = statusObj.getPath()
        full_path_list = full_path.split('/')[1:]
        relative_path = full_path[len(path)+1:]
        relative_path_list = relative_path.split('/')
        # Processing entry
        filename = relative_path_list[-1]
        # Needed or files will be both File & Dir objects
        relative_path_list = relative_path_list[:-1]
        parent = root
        i = len(path.split('/'))-1
        
        for d in relative_path_list :
          i += 1
          if d :
            full_pathOfd = '/'+'/'.join(full_path_list[:i]).strip()
            if d not in parent.getSubDirs() :
              parent.sub_dirs.append(Dir(full_pathOfd, "normal"))
            parent = parent.getDir(d)
        if os.path.isdir(full_path) :
          if full_path == parent.full_path :
            parent.msg_status = str(msg_status)
          elif filename not in parent.getSubDirs() :
            parent.sub_dirs.append(Dir(filename, str(msg_status)))
          else :
            tmp = parent.getDir(filename)
            tmp.msg_status = str(msg_status)
        else :
          parent.sub_dirs.append(File(full_path, str(msg_status)))
    return somethingModified and root
  
  def extractBT(self, bt, path):
    os.system('rm -rf %s'%path)
    bt.export(path=path, local=1)
    svn_path = self.getPortalObject().portal_preferences.getPreference('subversion_working_copy')
    if not svn_path :
      raise "Error: Please set Subversion working path in preferences"
    if svn_path[-1]!='/':
      svn_path+='/'
    svn_path += bt.getTitle()+'/'
    if path[-1]!='/':
      path+='/'
    # update working copy from repository
    self.update(svn_path)
    # svn del deleted files
    self.deleteOldFiles(svn_path, path)
    # add new files and copy
    self.addNewFiles(svn_path, path)
    # Clean up
    os.system('rm -rf %s'%path)
  
  # svn del files that have been removed in new dir
  def deleteOldFiles(self, old_dir, new_dir):
    # detect removed files
    output = commands.getoutput('export LC_ALL=c;diff -rq %s %s --exclude .svn | grep "Only in " | grep -v "svn-commit." | grep %s | cut -d" " -f3,4'%(new_dir, old_dir, old_dir)).replace(': ', '/')
    files_list = output.split('\n')
    # svn del
    for file in files_list:
      if file:
        try:
          LOG('SubversionTool', WARNING, 'svn del %s'%file)
          self.remove(file) 
        except:
          pass
  
  def addNewFiles(self, old_dir, new_dir):
    # detect created files
    output = commands.getoutput('export LC_ALL=c;diff -rq %s %s --exclude .svn | grep "Only in " | grep -v "svn-commit." | grep %s | cut -d" " -f3,4'%(new_dir, old_dir, old_dir)).replace(': ', '/')
    files_list = output.split('\n')
    # Copy files
    LOG('SubversionTool', WARNING, 'copy %s to %s'%(new_dir, old_dir))
    os.system('cp -af %s/* %s'%(new_dir, old_dir))
    # svn add
    for file in files_list:
      if file:
        try:
          LOG('SubversionTool', WARNING, 'svn add %s'%file.replace(new_dir, old_dir))
          self.add(file.replace(new_dir, old_dir))
        except:
          pass
  
  def treeToXML(self, item) :
    output = "<?xml version='1.0' encoding='iso-8859-1'?>"+ os.linesep
    output += "<tree id='0'>" + os.linesep
    output = self._treeToXML(item, output, 1, True)
    output += "</tree>" + os.linesep
    return output
  
  def _treeToXML(self, item, output, ident, first) :
    # Choosing a color coresponding to the status
    itemStatus = item.msg_status
    if itemStatus == 'added' :
      itemColor='green'
    elif itemStatus == 'modified' :
      itemColor='orange'
    elif itemStatus == 'deleted' :
      itemColor='red'
    else :
      itemColor='black'
      
    if isinstance(item, Dir) :
      for i in range(ident) :
        output += '\t'
      if first :
        output += '<item open="1" text="%s" id="%s" aCol="%s" '\
        'im0="folder.png" im1="folder_open.png" '\
        'im2="folder.png">'%(item.name,
item.full_path, itemColor,) + os.linesep
        first=False
      else :
        output += '<item text="%s" id="%s" aCol="%s" im0="folder.png" ' \
      'im1="folder_open.png" im2="folder.png">'%(item.name,
item.full_path, itemColor,) + os.linesep
      for it in item.sub_dirs:
        ident += 1
        output = self._treeToXML(item.getDir(it.name), output, ident,
first)
        ident -= 1
      for i in range(ident) :
        output += '\t'
      output += '</item>' + os.linesep
    else :
      for i in range(ident) :
        output += '\t'
      output += '<item text="%s" id="%s" aCol="%s" im0="document.png"/>'\
                %(item.name, item.full_path, itemColor,) + os.linesep
    return output
    
InitializeClass(SubversionTool)
