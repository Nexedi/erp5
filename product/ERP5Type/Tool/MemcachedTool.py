##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Vincent Pelletier <vincent@nexedi.com>
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

from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions, _dtmldir
from AccessControl import ClassSecurityInfo
from Globals import DTMLFile

MEMCACHED_TOOL_MODIFIED_FLAG_PROPERTY_ID = '_v_memcached_edited'

try:
  import memcache
except ImportError:
  memcache = None

def encodeKey(key):
  """
    Encode the key. The current encoding is not very good
    since it is not bijective. Implementing a bijective
    encoding is required.
  """
  # Memcached refuses characters which are below ' ' (included) in
  # ascii table. Just strip them here to avoid the raise.
  return ''.join([x for x in key if ord(x) > \
                              MEMCACHED_MINIMUM_KEY_CHAR_ORD])

if memcache is not None:
  # Real memcache tool
  import memcache
  import traceback
  from Shared.DC.ZRDB.TM import TM
  from Products.PythonScripts.Utility import allow_class
  from zLOG import LOG
  
  MARKER = tuple()
  UPDATE_ACTION = 'update'
  DELETE_ACTION = 'delete'
  MEMCACHED_MINIMUM_KEY_CHAR_ORD = ord(' ')
  
  class MemcachedDict(TM):
    """
      Present memcached similarly to a dictionary (not all method are
      available).
      Uses transactions to only update memcached at commit time.
      No conflict generation/resolution : last edit wins.
  
      TODO:
        - prove that concurency handling in event queuing is not needed
        - make picklable ?
    """
  
    def __init__(self, server_list=('127.0.0.1:11211', )):
      """
        Initialise properties :
        memcached_connection
          Connection to memcached.
        local_cache
          Dictionnary used as a connection cache with duration limited to
          transaction length.
        scheduled_action_dict
          Each key in this dictionary must be handled at transaction commit.
          Value gives the action to take :
            UPDATE_ACTION 
              Take value from local cache and send it to memcached.
            DELETE_ACTION
              Send a delete order to memcached.
      """
      self.local_cache = {}
      self.scheduled_action_dict = {}
      self.memcached_connection = memcache.Client(server_list)
  
    def __del__(self):
      """
        Close connection before deleting object.
      """
      self.memcached_connection.disconnect_all()
  
    def _finish(self, *ignored):
      """
        Actually modifies the values in memcached.
        This avoids multiple accesses to memcached during the transaction.
        Invalidate all local cache to make sure changes donc by other zopes
        would not be ignored.
      """
      try:
        for key, value in self.local_cache.iteritems():
          if getattr(value, MEMCACHED_TOOL_MODIFIED_FLAG_PROPERTY_ID, None):
            delattr(value, MEMCACHED_TOOL_MODIFIED_FLAG_PROPERTY_ID)
            self.scheduled_action_dict[key] = UPDATE_ACTION
        for key, action in self.scheduled_action_dict.iteritems():
          if action is UPDATE_ACTION:
            self.memcached_connection.set(encodeKey(key), self.local_cache[key], 0)
          elif action is DELETE_ACTION:
            self.memcached_connection.delete(encodeKey(key), 0)
      except:
        LOG('MemcachedDict', 0, 'An exception occured during _finish : %s' % (traceback.format_exc(), ))
      self.scheduled_action_dict.clear()
      self.local_cache.clear()
  
    def _abort(self, *ignored):
      """
        Cleanup the action dict and invalidate local cache.
      """
      self.local_cache.clear()
      self.scheduled_action_dict.clear()
  
    def __getitem__(self, key):
      """
        Get an item from local cache, otherwise from memcached.
      """
      # We need to register in this function too to be able to flush cache at 
      # transaction end.
      self._register()
      encoded_key = encodeKey(key)
      result = self.local_cache.get(key, MARKER)
      if result is MARKER:
        result = self.memcached_connection.get(encoded_key)
        if result is None:
          raise KeyError, 'Key %s (was %s) not found.' % (encoded_key, key)
        self.local_cache[key] = result
      return result
  
    def __setitem__(self, key, value):
      """
        Set an item to local cache and schedule update of memcached.
      """
      self._register()
      self.scheduled_action_dict[key] = UPDATE_ACTION
      self.local_cache[key] = value
  
    def __delitem__(self, key):
      """
        Schedule key for deletion in memcached.
        Set the value to None in local cache to avoid gathering the value
        from memcached.
        Never raises KeyError because action is delayed.
      """
      self._register()
      self.scheduled_action_dict[key] = DELETE_ACTION
      self.local_cache[key] = None
  
    def set(self, key, value):
      """
        Set an item to local cache and schedule update of memcached.
      """
      return self.__setitem__(key, value)
  
    def get(self, key, default=None):
      """
        Get an item from local cache, otherwise from memcached.
        Note that because __getitem__ never raises error, 'default' will never
        be used (None will be returned instead).
      """
      try:
        return self.__getitem__(key)
      except KeyError:
        return default

  class SharedDict:
    """
      Class to make possible for multiple "users" to store data in the same
      dictionary without risking to overwrite other's data.
      Each "user" of the dictionary must get an instance of this class.
  
      TODO:
        - handle persistence ?
    """
  
    def __init__(self, dictionary, prefix):
      """
        dictionary
          Instance of dictionary to share.
        prefix
          Prefix used by the "user" owning an instance of this class.
      """
      self._dictionary = dictionary
      self.prefix = prefix
  
    def _prefixKey(self, key):
      """
        Prefix key with self.prefix .
      """
      if not isinstance(key, basestring):
        raise TypeError, 'Key %s is not a string. Only strings are supported as key in SharedDict' % (repr(key), )
      return '%s_%s' % (self.prefix, key)
  
    def __getitem__(self, key):
      """
        Get item from memcached.
      """
      return self._dictionary.__getitem__(self._prefixKey(key))
    
    def __setitem__(self, key, value):
      """
        Put item in memcached.
      """
      self._dictionary.__setitem__(self._prefixKey(key), value)
  
    def __delitem__(self, key):
      """
        Delete item from memcached.
      """
      self._dictionary.__delitem__(self._prefixKey(key))
  
    # These are the method names called by zope
    __guarded_setitem__ = __setitem__
    __guarded_getitem__ = __getitem__
    __guarded_delitem__ = __delitem__
  
    def get(self, key, default=None):
      """
        Get item from memcached.
      """
      return self._dictionary.get(self._prefixKey(key), default)
  
    def set(self, key, value):
      """
        Put item in memcached.
      """
      self._dictionary.set(self._prefixKey(key), value)
  
  allow_class(SharedDict)
  
  class MemcachedTool(BaseTool):
    """
      Memcached interface available as a tool.
    """
    id = "portal_memcached"
    meta_type = "ERP5 Memcached Tool"
    portal_type = "Memcached Tool"
    
    security = ClassSecurityInfo()
    manage_options = ({'label': 'Configure',
                       'action': 'memcached_tool_configure',
                      },) + BaseTool.manage_options
  
    memcached_tool_configure = DTMLFile('memcached_tool_configure', _dtmldir)
  
    def _getMemcachedDict(self):
      """
        Return used memcached dict.
        Create it if does not exist.
      """
      dictionary = getattr(self, '_v_memcached_dict', None)
      if dictionary is None:
        dictionary = MemcachedDict(self.getServerAddressList())
        self._v_memcached_dict = dictionary
      return dictionary
  
    security.declareProtected(Permissions.AccessContentsInformation, 'getMemcachedDict')
    def getMemcachedDict(self, key_prefix):
      """
        Returns an object which can be used as a dict and which gets from/stores
        to memcached server.
        
        key_prefix
          Mendatory argument allowing different tool users from sharing the same
          dictionary key namespace.
      """
      return SharedDict(dictionary=self._getMemcachedDict(), prefix=key_prefix)
  
    security.declareProtected(Permissions.ModifyPortalContent, 'setServerAddress')
    def setServerAddress(self, value):
      """
        Set a memcached server address.
      """
      self.setServerAddressList([value, ])
      self.server_address_list = [value, ]
      self._v_memcached_dict = None
  
    security.declareProtected(Permissions.AccessContentsInformation, 'getServerAddress')
    def getServerAddress(self):
      """
        Return server address.
      """
      return self.getServerAddressList()[0]
    
    def getServerAddressList(self):
      """
        Get the list of memcached servers to use.
        Defaults to ['127.0.0.1:11211', ].
      """
      return getattr(self, 'server_address_list', ['127.0.0.1:11211', ])

    def setServerAddressList(self, value):
      """
        Set the list of memcached servers to use.

        Upon server address change, force next access to memcached dict to
        reconnect to new ip.

        This is safe in multi zope environment, since we modify self which is
        persistent. Then all zopes will have to reload this tool instance, and
        loose their volatile properties in the process, which will force them
        to reconnect to memcached.
      """
      self.server_address_list = value
      self._v_memcached_dict = None

else:  
  # Placeholder memcache tool
  class MemcachedTool(BaseTool):
    """
      Dummy MemcachedTool placeholder.
    """
    id = "portal_memcached"
    meta_type = "ERP5 Memcached Tool"
    portal_type = "Memcached Tool"
    title = "DISABLED"

    security = ClassSecurityInfo()
    manage_options = ({'label': 'Configure',
                       'action': 'memcached_tool_configure',
                      },) + BaseTool.manage_options

    def failingMethod(self, *args, **kw):
      """
        if this function is called and memcachedtool is disabled, fail loudly
        with a meaningfull message.
      """
      raise RuntimeError, 'MemcachedTool is disabled. You should ask the'\
        ' server administrator to enable it by installing python-memcached.'

    setServerAddress = failingMethod
    getServerAddress = failingMethod
    getServerAddressList = failingMethod
    setServerAddressList = failingMethod
    memcached_tool_configure = failingMethod
    getMemcachedDict = failingMethod
