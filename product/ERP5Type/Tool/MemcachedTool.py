# -*- coding: utf-8 -*-
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
from six import string_types as basestring
from Products.ERP5Type.Utils import str2bytes
import time
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions, _dtmldir
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import DTMLFile, InitializeClass
from quopri import encodestring
import six

MEMCACHED_TOOL_MODIFIED_FLAG_PROPERTY_ID = '_v_memcached_edited'
class _MemcacheTool(BaseTool):
  id = "portal_memcached"
  meta_type = "ERP5 Memcached Tool"
  portal_type = "Memcached Tool"
  title = "Memcached Plugins"
  manage_options = (
    {
      'label': 'Configure',
      'action': 'memcached_tool_configure',
    },
  ) + BaseTool.manage_options

try:
  import memcache
except ImportError:
  memcache = None

def encodeKey(key):
  """
    Encode the key like 'Quoted Printable'.
  """
  # According to the memcached's protocol.txt, the key cannot contain
  # control characters and white spaces.
  return encodestring(str2bytes(key), True).replace(b'\n', b'').replace(b'\r', b'')

if memcache is not None:
  # Real memcache tool
  from Shared.DC.ZRDB.TM import TM
  from Products.PythonScripts.Utility import allow_class
  from zLOG import LOG, INFO

  MARKER = object()
  DELETE_ACTION = 0
  UPDATE_ACTION = 1

  _client_pool = {}
  def getClient(server_list, server_max_key_length, server_max_value_length):
    """
    Pool memcache.Client instances.

    This is possible as there is no such thing as a database snapshot on
    memcached connections (unlike, for example, mysql).
    Also, memcached.Client instance are thread-safe (by inheriting from
    threading.local), so we only need one instance per parameter set (and
    we use few enough parameter variants to make this manageable).
    """
    key = (
      tuple(sorted(server_list)),
      server_max_key_length,
      server_max_value_length,
    )
    try:
      return _client_pool[key]
    except KeyError:
      client = _client_pool[key] = memcache.Client(
        server_list,
        pickleProtocol=-1, # use the highest available version
        server_max_key_length=server_max_key_length,
        server_max_value_length=server_max_value_length,
      )
      return client

  class MemcachedDict(TM):
    """
      Present memcached similarly to a dictionary (not all method are
      available).
      Uses transactions to only update memcached at commit time.
      No conflict generation/resolution : last edit wins.
    """
    def __init__(self, server_list, expiration_time=0,
          server_max_key_length=memcache.SERVER_MAX_KEY_LENGTH,
          server_max_value_length=memcache.SERVER_MAX_VALUE_LENGTH,
        ):
      """
        server_list (tuple of strings)
          Servers to connect to, in 'host:port' format.
        expiration_time (int)
          Entry expiration time. See "Expiration times" in memcache protocol
          spec. Summary:
          0 = never
          less than 60*60*24*30 = time starting at entry creation/update
          more = absolute unix timestamp
        server_max_key_length (int)
          Maximum key length. Storing larger keys will cause an exception to be
          raised.
        server_max_value_length (int)
          Maximum value length. Storing larger values will cause an exception to
          be raised.
      """
      # connection cache with duration limited to transaction length.
      self.local_cache = {}
      # Each key in scheduled_action_dict must be handled at commit.
      # UPDATE_ACTION: send local_cache value to server
      # DELETE_ACTION: delete on server
      self.scheduled_action_dict = {}
      self.server_list = server_list
      # see "Expiration times" from memcached protocol docs
      # (this simulates relative expiration time greater than 30 days)
      self.expiration_time_since_epoch = expiration_time >= 2592000
      self.expiration_time = expiration_time
      self.server_max_key_length = server_max_key_length
      self.server_max_value_length = server_max_value_length
      self.memcached_connection = getClient(
        server_list,
        server_max_key_length=server_max_key_length,
        server_max_value_length=server_max_value_length,
      )

    def _finish(self, *ignored):
      """
        Actually modifies the values in memcached.
        This avoids multiple accesses to memcached during the transaction.
        Invalidate all local cache to make sure changes donc by other zopes
        would not be ignored.
      """
      try:
        expiration_time = self.expiration_time
        if self.expiration_time_since_epoch:
          expiration_time += time.time()
        for key, value in six.iteritems(self.local_cache):
          if getattr(value, MEMCACHED_TOOL_MODIFIED_FLAG_PROPERTY_ID, None):
            delattr(value, MEMCACHED_TOOL_MODIFIED_FLAG_PROPERTY_ID)
            self.scheduled_action_dict[key] = UPDATE_ACTION
        for key, action in six.iteritems(self.scheduled_action_dict):
          encoded_key = encodeKey(key)
          if action is UPDATE_ACTION:
            self.memcached_connection.set(
              encoded_key,
              self.local_cache[key],
              expiration_time,
            )
          elif action is DELETE_ACTION:
            self.memcached_connection.delete(encoded_key, 0)
      except Exception:
        # This is a cache. Failing to push data to server must be fine, as long as
        # cleanup succeeds.
        LOG('MemcachedDict', INFO, 'An exception occured during _finish', error=True)
      self.__cleanup()

    def _abort(self, *ignored):
      self.__cleanup()

    def __cleanup(self):
      self.local_cache.clear()
      self.scheduled_action_dict.clear()

    def __getitem__(self, key):
      """
        Get an item from local cache, otherwise from memcached.
      """
      # We need to register in this function too to be able to flush cache at
      # transaction end.
      self._register()
      if self.scheduled_action_dict.get(key) == DELETE_ACTION:
        raise KeyError
      result = self.local_cache.get(key, MARKER)
      if result is MARKER:
        encoded_key = encodeKey(key)
        try:
          result = self.memcached_connection.get(encoded_key)
        except memcache.Client.MemcachedConnectionError:
          LOG('MemcacheTool', INFO, 'get command to memcached server (%r) failed' % (self.server_list,), error=True)
          raise KeyError
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
      return self.__setitem__(key, value)

    def get(self, key, default=None):
      try:
        return self.__getitem__(key)
      except KeyError:
        return default

  class SharedDict(object):
    """
      Class to make possible for multiple "users" to store data in the same
      dictionary without risking to overwrite other's data.
      Each "user" of the dictionary must get an instance of this class.
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
      if not isinstance(key, basestring):
        raise TypeError('Key %r is not a string. Only strings are supported as key in SharedDict' % (key,))
      return '%s_%s' % (self.prefix, key)

    def __getitem__(self, key):
      return self._dictionary.__getitem__(self._prefixKey(key))

    def __setitem__(self, key, value):
      self._dictionary.__setitem__(self._prefixKey(key), value)

    def __delitem__(self, key):
      self._dictionary.__delitem__(self._prefixKey(key))

    # These are the method names called by zope
    __guarded_setitem__ = __setitem__
    __guarded_getitem__ = __getitem__
    __guarded_delitem__ = __delitem__

    def get(self, key, default=None):
      return self._dictionary.get(self._prefixKey(key), default)

    def set(self, key, value):
      self._dictionary.set(self._prefixKey(key), value)

  allow_class(SharedDict)

  class MemcachedTool(_MemcacheTool):
    """
      Memcached interface available as a tool.
    """
    security = ClassSecurityInfo()
    memcached_tool_configure = DTMLFile('memcached_tool_configure', _dtmldir)
    erp5_site_global_id = ''

    security.declareProtected(Permissions.AccessContentsInformation, 'getMemcachedDict')
    def getMemcachedDict(self, key_prefix, plugin_path):
      """
        Returns an object which can be used as a dict and which gets from/stores
        to memcached server.

        key_prefix
          Mandatory argument allowing different tool users to share the same
          dictionary key namespace.

        plugin_path
          relative_url of dedicated Memcached Plugin
      """
      memcached_plugin = self.restrictedTraverse(plugin_path, None)
      if memcached_plugin is None:
        raise ValueError('Memcached Plugin does not exists: %r' % (
          plugin_path, ))
      global_prefix = self.erp5_site_global_id
      if global_prefix:
        key_prefix = global_prefix + '_' + key_prefix
      return SharedDict(memcached_plugin.getConnection(), prefix=key_prefix)

  InitializeClass(MemcachedTool)
else:
  # Placeholder memcache tool
  class MemcachedTool(_MemcachedTool):
    """
      Dummy MemcachedTool placeholder.
    """
    title = "DISABLED"

    security = ClassSecurityInfo()

    def failingMethod(self, *args, **kw):
      """
        if this function is called and memcachedtool is disabled, fail loudly
        with a meaningfull message.
      """
      raise RuntimeError('MemcachedTool is disabled. You should ask the'
        ' server administrator to enable it by installing python-memcached.')

    memcached_tool_configure = failingMethod
    getMemcachedDict = failingMethod
