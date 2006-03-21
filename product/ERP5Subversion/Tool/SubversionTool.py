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
import os
from DateTime import DateTime
from cPickle import dumps, loads
from App.config import getConfiguration
from zExceptions import Unauthorized

try:
  from base64 import b64encode, b64decode
except ImportError:
  from base64 import encodestring as b64encode, decodestring as b64decode
  
class File :
  # Constructor
  def __init__(self, fullPath) :
    self.fullPath = fullPath
    self.fileName = fullPath.split('/')[-1]

  # return the file name
  def getName(self) :
    return self.fileName
  
    # return the file path
  def getFullPath(self) :
    return self.fullPath
## End of File Class

class Dir :
  # Constructor
  def __init__(self, fullPath) :
    self.fullPath = fullPath
    self.dirName = fullPath.split('/')[-1]
    self.subdirs = [] # list of sub directories

  # return directory's short name
  def getName(self) :
    return self.dirName
  
  # return directory's path
  def getFullPath(self) :
    return self.fullPath

  # return a list of sub directories' names
  def getSubDirs(self) :
    return [d.getName() for d in self.subdirs]

  # add a sub directory to the list
  def addSubDir(self, item) :
    self.subdirs.append(item)

  # return directory in subdirs given its name
  def getDir(self, name):
    for d in self.subdirs:
      if d.getName() == name:
        return d
## End of Dir Class
  
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
    trust_item_list, permanent = loads(b64decode(login))
    return dict(trust_item_list), permanent
    
  security.declareProtected(Permissions.ManagePortal, 'acceptSSLServer')
  def acceptSSLServer(self, trust_dict, permanent=False):
    """Accept a SSL server.
    """
    # Get existing trust information.
    trust_list = []
    request = self.REQUEST
    cookie = request.get(self.ssl_trust_cookie_name)
    if cookie:
      trust.append(cookie)
    # Set the cookie.
    response = request.RESPONSE
    trust_list.append(self._encodeSSLTrust(trust_dict, permanent))
    value = ','.join(trust_list)
    expires = (DateTime() + 1).toZone('GMT').rfc822()
    response.setCookie(self.ssl_trust_cookie_name, value, path = '/', expires = expires)

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
    return client.update(self._getWorkingPath(path))

  security.declareProtected('Import/Export objects', 'add')
  def add(self, path):
    """Add a file or a directory.
    """
    client = self._getClient()
    return client.add(self._getWorkingPath(path))

  security.declareProtected('Import/Export objects', 'remove')
  def remove(self, path):
    """Remove a file or a directory.
    """
    client = self._getClient()
    return client.remove(self._getWorkingPath(path))

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
    return client.diff(self._getWorkingPath(path))

  security.declareProtected('Import/Export objects', 'revert')
  def revert(self, path):
    """Revert local changes in a file or a directory.
    """
    client = self._getClient()
    return client.revert(self._getWorkingPath(path))

  security.declareProtected('Import/Export objects', 'checkin')
  def checkin(self, path, log_message = None):
    """Commit local changes.
    """
    client = self._getClient(log_message = log_message)
    return client.checkin(self._getWorkingPath(path))

  security.declareProtected('Import/Export objects', 'status')
  def status(self, path, **kw):
    """Get status.
    """
    client = self._getClient()
    return client.status(self._getWorkingPath(path), **kw)
  
  def getModifiedTree(self, path) :
    # Remove trailing slash if it's present
    if path[-1]=="/" :
      path = path[:-1]
    
    #root = Dir(path.split('/')[-1])
    root = Dir(path)

    for statusObj in self.status(path) :
      # (normal, added, modified, deleted)
      msgStatus = statusObj.getTextStatus()
      f = file('/tmp/py.log','w')
      if str(msgStatus) != "normal" :
        full_path = statusObj.getPath()
        full_path_list = full_path.split('/')[1:]
        f.write('full_path_list = %s\n' % full_path_list)
        relative_path = full_path[len(path)+1:]
        relative_path_list = relative_path.split('/')
        f.write('relative_path_list = %s\n' % relative_path_list)
        # Processing entry
        filename = relative_path_list[-1]
        # Needed or files will be both File & Dir objects
        relative_path_list = relative_path_list[:-1]
        parent = root
        i = len(path.split('/'))-1
        
        for d in relative_path_list :
          i += 1
          if d :
            if d not in parent.getSubDirs():
              f.write('d is = %s\n'% d)
              f.write('adding subdir %s to parent %s\n'% ('/'+'/'.join(full_path_list[:i]).strip(), parent.getFullPath()))
              parent.addSubDir(Dir('/'+'/'.join(full_path_list[:i]).strip()))
            parent = parent.getDir(d)
        parent.addSubDir(File(full_path))
        f.close()
    return root
            
  def treeToXML(self, item) :
    output = "<?xml version='1.0' encoding='iso-8859-1'?>"+ os.linesep
    output += "<tree id='0'>" + os.linesep
    output = self._treeToXML(item, output, 1)
    output += "</tree>" + os.linesep
    return output
  
  def _treeToXML(self, item, output, ident) :
    if isinstance(item, Dir) :
      for i in range(ident) :
        output += '\t'
      output += '<item text="%s" id="%s" im0="folderClosed.gif" im1="folderOpen.gif" im2="folderClosed.gif">'%(item.getName(), item.getFullPath(),) + os.linesep
      for it in item.subdirs:
        ident += 1
        output = self._treeToXML(item.getDir(it.getName()), output, ident)
        ident -= 1
      for i in range(ident) :
        output += '\t'
      output += '</item>' + os.linesep
    else :
      for i in range(ident) :
        output += '\t'
      output += '<item text="%s" id="%s" im0="leaf.gif" im1="leaf.gif" im2="leaf.gif"/>'%(item.getName(), item.getFullPath(),) + os.linesep

    return output
    
InitializeClass(SubversionTool)
