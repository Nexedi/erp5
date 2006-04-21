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

from Acquisition import Implicit

import time, os, time
from Products.ERP5Type.Utils import convertToUpperCase
from MethodObject import Method
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.PythonScripts.Utility import allow_class
from tempfile import mktemp

try:
  import pysvn
  

  class SubversionError(Exception):
    """The base exception class for the Subversion interface.
    """
    pass
    
  class SubversionInstallationError(SubversionError):
    """Raised when an installation is broken.
    """
    pass
    
  class SubversionTimeoutError(SubversionError):
    """Raised when a Subversion transaction is too long.
    """
    pass
  
  class SubversionLoginError(SubversionError):
    """Raised when an authentication is required.
    """
    # Declarative Security
    security = ClassSecurityInfo()
    
    def __init__(self, realm = None):
      self._realm = realm
  
    security.declarePublic('getRealm')
    def getRealm(self):
      return self._realm
      
  class SubversionSSLTrustError(SubversionError):
    """Raised when a SSL certificate is not trusted.
    """
    # Declarative Security
    security = ClassSecurityInfo()
    
    def __init__(self, trust_dict = None):
      self._trust_dict = trust_dict
      
    security.declarePublic('getTrustDict')
    def getTrustDict(self):
      return self._trust_dict
  
  class Callback:
    """The base class for callback functions.
    """
    def __init__(self, client):
      self.client = client
  
    def __call__(self, *args):
      pass
  
  class CancelCallback(Callback):
    def __call__(self):
      current_time = time.time()
      if current_time - self.client.creation_time > self.client.getTimeout():
        raise SubversionTimeoutError, 'too long transaction'
        #return True
      return False
  
  class GetLogMessageCallback(Callback):
    def __call__(self):
      message = self.client.getLogMessage()
      if message:
        return True, message
      return False, ''
  
  class GetLoginCallback(Callback):
    def __call__(self, realm, username, may_save):
      user, password = self.client.getLogin(realm)
      if not username or not password:
        self.client.setException(SubversionLoginError(realm))
        return False, '', '', False
      return True, user, password, False
  
  class NotifyCallback(Callback):
    def __call__(self, event_dict):
      # FIXME: should accumulate information for the user
      pass
  
  class SSLServerTrustPromptCallback(Callback):
    def __call__(self, trust_dict):
      trust, permanent = self.client.trustSSLServer(trust_dict)
      if not trust:
        self.client.setException(SubversionSSLTrustError(trust_dict))
        return False, 0, False
      # XXX SSL server certificate failure bits are not defined in pysvn.
      # 0x8 means that the CA is unknown.
      return True, 0x8, permanent

  # Wrap objects defined in pysvn so that skins have access to attributes in the ERP5 way.
  class Getter(Method):
    def __init__(self, key):
      self._key = key
  
    def __call__(self, instance):
      value = getattr(instance._obj, self._key)
      if type(value) == type(u''):
        value = value.encode('utf-8')
      #elif isinstance(value, pysvn.Entry):
      elif str(type(value)) == "<type 'entry'>":
        value = Entry(value)
      #elif isinstance(value, pysvn.Revision):
      elif str(type(value)) == "<type 'revision'>":
        value = Revision(value)
      return value

  def initializeAccessors(klass):
    klass.security = ClassSecurityInfo()
    klass.security.declareObjectPublic()
    for attr in klass.attribute_list:
      name = 'get' + convertToUpperCase(attr)
      print name
      setattr(klass, name, Getter(attr))
      klass.security.declarePublic(name)
    InitializeClass(klass)

  class ObjectWrapper(Implicit):
    attribute_list = ()
    
    def __init__(self, obj):
      self._obj = obj
  
  class Status(ObjectWrapper):
    # XXX Big Hack to fix a bug
    __allow_access_to_unprotected_subobjects__ = 1
    attribute_list = ('path', 'entry', 'is_versioned', 'is_locked', 'is_copied', 'is_switched', 'prop_status', 'text_status', 'repos_prop_status', 'repos_text_status')
  initializeAccessors(Status)
  
  class Entry(ObjectWrapper):
    attribute_list = ('checksum', 'commit_author', 'commit_revision', 'commit_time',
                      'conflict_new', 'conflict_old', 'conflict_work', 'copy_from_revision',
                      'copy_from_url', 'is_absent', 'is_copied', 'is_deleted', 'is_valid',
                      'kind', 'name', 'properties_time', 'property_reject_file', 'repos',
                      'revision', 'schedule', 'text_time', 'url', 'uuid')

  class Revision(ObjectWrapper):
    attribute_list = ('kind', 'date', 'number')
  initializeAccessors(Revision)

  
  class SubversionClient(Implicit):
    """This class wraps pysvn's Client class.
    """
    log_message = None
    timeout = 60 * 5
    
    def __init__(self, container, **kw):
      self.client = pysvn.Client()
      self.client.set_auth_cache(0)
      obj = self.__of__(container)
      self.client.callback_cancel = CancelCallback(obj)
      self.client.callback_get_log_message = GetLogMessageCallback(obj)
      self.client.callback_get_login = GetLoginCallback(obj)
      self.client.callback_notify = NotifyCallback(obj)
      self.client.callback_ssl_server_trust_prompt = SSLServerTrustPromptCallback(obj)
      self.creation_time = time.time()
      self.__dict__.update(kw)
      self.exception = None

    def getLogMessage(self):
      return self.log_message
    
    def getLogin(self, realm):
      return self.aq_parent._getLogin(realm)

    def getTimeout(self):
      return self.timeout
        
    def trustSSLServer(self, trust_dict):
      return self.aq_parent._trustSSLServer(trust_dict)

    def setException(self, exc):
      self.exception = exc

    def getException(self):
      return self.exception
    
    def checkin(self, path, log_message, recurse):
      try:
        return self.client.checkin(path, log_message=log_message or 'none', recurse=recurse)
      except pysvn.ClientError, error:
        excep = self.getException()
        if excep:
          raise excep
        else:
          raise error

    def update(self, path):
      try:
        return self.client.update(path)
      except pysvn.ClientError, error:
        excep = self.getException()
        if excep:
          raise excep
        else:
          raise error
        
    def status(self, path, **kw):
      # Since plain Python classes are not convenient in Zope, convert the objects.
      return [Status(x) for x in self.client.status(path, **kw)]
    
    def diff(self, path, revision1, revision2):
      tmp = mktemp()
      os.system('mkdir -p %s'%tmp)
      if not revision1 or not revision2:
        diff = self.client.diff(tmp_path=tmp, url_or_path=path, recurse=False)
      else:
        diff = self.client.diff(tmp_path=tmp, url_or_path=path, recurse=False, revision1=pysvn.Revision(pysvn.opt_revision_kind.number,revision1), revision2=pysvn.Revision(pysvn.opt_revision_kind.number,revision2))
      # clean up temp dir
      os.system('rm -rf %s'%tmp)
      return diff
    
    def revert(self, path):
      return self.client.revert(path)
    
    def log(self, path):
      try:
        log_list = self.client.log(path)
      except pysvn.ClientError, error:
        if 'path not found' in error.args[0]:
          return
        excep = self.getException()
        if excep:
          raise excep
        else:
          raise error
      # Edit list to make it more usable in zope
      for rev_dict in log_list:
        rev_dict['revision'] = rev_dict['revision'].number
        rev_dict['date'] = time.ctime(rev_dict['date'])
      return log_list
        
    def add(self, path):
      return self.client.add(path=path, force=True)

    def info(self, path):
      try:
        entry = self.client.info(path=path)
      except pysvn.ClientError, error:
        excep = self.getException()
        if excep:
          raise excep
        else:
          raise error
      # transform entry to dict to make it more usable in zope
      members_tuple=('url', 'uuid', 'revision', 'kind', 'commit_author', 'commit_revision', 'commit_time',)
      entry_dict = dict([(member,getattr(entry,member)) for member in members_tuple])
      entry_dict['revision'] = entry_dict['revision'].number
      entry_dict['commit_revision'] = entry_dict['commit_revision'].number
      entry_dict['commit_time'] = time.ctime(entry_dict['commit_time'])
      return entry_dict
      
    def ls(self, path):
      try:
        dict_list = self.client.ls(url_or_path=path, recurse=False)
      except pysvn.ClientError, error:
        if 'non-existent' in error.args[0]:
          return
        excep = self.getException()
        if excep:
          raise excep
        else:
          raise error
       #Modify the list to make it more usable in zope
      for dict in dict_list:
        dict['created_rev']=dict['created_rev'].number
        dict['time']=time.ctime(dict['time'])
      return dict_list

    def cleanup(self, path):
      return self.client.cleanup(path=path)

    def remove(self, path):
      return self.client.remove(url_or_path=path, force=True)

  def newSubversionClient(container, **kw):
    return SubversionClient(container, **kw).__of__(container)
    
  InitializeClass(SubversionSSLTrustError)
  allow_class(SubversionSSLTrustError)
  InitializeClass(SubversionLoginError)
  allow_class(SubversionLoginError)
  
except ImportError:
  from zLOG import LOG, WARNING
  LOG('SubversionTool', WARNING,
      'could not import pysvn; until pysvn is installed properly, this tool will not work.')
  def newSubversionClient(container, **kw):
    raise SubversionInstallationError, 'pysvn is not installed'
