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

from Acquisition import Implicit
import time
from Products.ERP5Type.Utils import convertToUpperCase
from MethodObject import Method
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

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
    def __init__(self, realm = None):
      self._realm = realm
  
    def getRealm(self):
      return self._realm
      
  class SubversionSSLTrustError(SubversionError):
    """Raised when a SSL certificate is not trusted.
    """
    def __init__(self, trust_dict = None):
      self._trust_dict = trust_dict
  
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
      if user is None:
        raise SubversionLoginError(realm)
        #return False, '', '', False
      return True, user, password, False
  
  class NotifyCallback(Callback):
    def __call__(self, event_dict):
      # FIXME: should accumulate information for the user
      pass
  
  class SSLServerTrustPromptCallback(Callback):
    def __call__(self, trust_dict):
      trust, permanent = self.client.trustSSLServer(trust_dict)
      if not trust:
        raise SubversionSSLTrustError(trust_dict)
        #return False, 0, False
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
      elif isinstance(value, pysvn.Entry):
        value = Entry(value)
      elif isinstance(value, pysvn.Revision):
        value = Revision(value)
      return value

  def initializeAccessors(klass):
    klass.security = ClassSecurityInfo()
    for attr in klass.attribute_list:
      name = 'get' + convertToUpperCase(attr)
      setattr(klass, name, Getter(attr))
      klass.security.declarePublic(name)
    InitializeClass(Status)

  class ObjectWrapper(Implicit):
    attribute_list = ()
    
    def __init__(self, obj):
      self._obj = obj
  
  class Status(ObjectWrapper):
    attribute_list = ('path', 'entry', 'is_versioned', 'is_locked', 'is_copied', 'is_switched',
                      'prop_status', 'text_status', 'repos_prop_status', 'repos_text_status')
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
    
    def __init__(self, **kw):
      self.client = pysvn.Client()
      self.client.set_auth_cache(0)
      self.client.callback_cancel = CancelCallback(self)
      self.client.callback_get_log_message = GetLogMessageCallback(self)
      self.client.callback_get_login = GetLoginCallback(self)
      self.client.callback_notify = NotifyCallback(self)
      self.client.callback_ssl_server_trust_prompt = SSLServerTrustPromptCallback(self)
      self.creation_time = time.time()
      self.__dict__.update(kw)

    def getLogMessage(self):
      return self.log_message

    def getTimeout(self):
      return self.timeout

    def getLogin(self, realm):
      return self.aq_parent._getLogin(realm)

    def trustSSLServer(self, trust_dict):
      return self.aq_parent._trustSSLServer(trust_dict)

    def status(self, path, **kw):
      # Since plain Python classes are not convenient in Zope, convert the objects.
      return [Status(x) for x in self.client.status(path, **kw)]

  def newSubversionClient(container, **kw):
    return SubversionClient(**kw).__of__(container)
    
except ImportError:
  LOG('SubversionTool', WARNING,
      'could not import pysvn; until pysvn is installed properly, this tool will not function.')
  def newSubversionClient(container, **kw):
    raise SubversionInstallationError, 'pysvn is not installed'
