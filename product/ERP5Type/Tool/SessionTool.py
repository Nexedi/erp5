# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002, 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Ivan Tyagov <ivan@nexedi.com>
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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Acquisition import aq_base
from UserDict import UserDict

# the ERP5 cache factory used as a storage
SESSION_CACHE_FACTORY = 'erp5_session_cache'
SESSION_SCOPE = 'SESSION'

# =24 hours, really last default duration value set if not defined in storage
DEFAULT_SESSION_DURATION = 86400

_marker=[]

# global storage plugin
storage_plugin = None

class Session(UserDict):
  """ Session acts as a plain python dictionary stored in respecitve Cache Factory/Cache Plugin.
      Depending on cache plugin used as a storage some restrictions may apply.
      Please be AWARE that there's no security checks applied. """

  # we have our own security policy and do not want Zope's
  _guarded_writes = 1 
  __allow_access_to_unprotected_subobjects__ = 1

  # XXX (dirty hack): we shouldn't need to explicitly set uid here
  uid = 'NULL'

  # used to set duration of session
  session_duration = None

  def _updatecontext(self, aq_context):
    """ Update current aquisition context. 
         This makes only sense for local RAM Session."""
    pass

  def _updateSessionDuration(self, session_duration):
    self.session_duration = int(session_duration)

  def _updateSessionId(self, session_id):
    self.session_id = session_id

  def __str__(self):
    return self.__repr__()

  def edit(self, **kw):
    """ Edit session object. """
    for key, item in kw.items():
      self.__setitem__(key, item)

class RamSession(Session):
  """ Local RAM Session dictionary """

  # a handle to current aquisition context
  _aq_context = None

  def _updatecontext(self, aq_context):
    """ Update current aquisition context. """
    self._aq_context = aq_context

# disabled as session should be dictionary like 
#  def __getattr__(self, key, default=_marker):
#    if key in self.data:
#      return self.__getitem__(key)
#    if default is not _marker:
#      return default
#    raise AttributeError, key

  def __getitem__(self, key):
    if key in self.data:
      value = self.data[key]
      if hasattr(value, '__of__'):
        # returned it wrapped in aquisition context
        value = value.__of__(self._aq_context)
      return value
    raise KeyError, key

  def __setitem__(self, key, item):
    # save value without its acquisition context
    Session.__setitem__(self, key, aq_base(item))

class DistributedSession(Session):
  """ Distributed Session dictionary.
      It uses DistributedRamCache plugins."""

  # session_id used to get respective dictionary from memcached
  session_id = None

  def _updateStorage(self):
    """ Update backend storage. """
    global storage_plugin
    storage_plugin.set(self.session_id, \
                       SESSION_SCOPE, \
                       value = self, \
                       cache_duration = getattr(self, 'session_duration', DEFAULT_SESSION_DURATION)) 

  # need to override methods that change session so changes are transparently sent to backend storage
  def __setitem__(self, key, item):
    Session.__setitem__(self, key, aq_base(item))
    self._updateStorage()

  def __delitem__(self, key):
    Session.__delitem__(self, key)
    self._updateStorage()

  def clear(self):
    Session.clear(self)
    self._updateStorage()

  def update(self, dict=None, **kwargs):
    Session.update(self, dict, **kwargs)
    self._updateStorage()

  def setdefault(self, key, failobj=None): 
    Session.setdefault(self, key, failobj)
    self._updateStorage()

  def  pop(self, key, *args):
    Session.pop(self, key, *args)
    self._updateStorage()

  def popitem(self):
    Session.popitem(self)
    self._updateStorage()


class SessionTool(BaseTool):
  """ Using this tool you can get a Session object by providing 
      your own generated session_id. 

      This session object can be used anywhere in Zope / ERP5 environment. 
      It can be local RAM based or Distributed (memcached). 
      Its type depends on the type of cache plugin used under Cache Factory defined
      as string in SESSION_CACHE_FACTORY and its first (and only) Cache Plugin. 
      You do not need to initialize it as this tool will initialize it as a plain dictionary for you.

      Example:

      session_id = '1234567'
      session = context.portal_sessions[session_id]
      session['shopping_cart'] = newTempOrder(context, '987654321') # will work only for local RAM sessions
      (you can also use 'session.edit(shopping_cart= newTempOrder(context, '987654321'))' )

      (later in another script you can acquire shopping_cart):

      session_id = '1234567'
      session = context.portal_sessions[session_id]
      shopping_cart = session['shopping_cart']

      Please note that:
       - developer is responsible for handling an unique sessiond_id (using cookies for example). 
       - it's not recommended to store in portal_sessions ZODB persistent objects because in order 
       to store them in Local RAM portal_sessions tool will remove aquisition wrapper. At "get" 
       request they'll be returend wrapped. 
       - developer can store temporary RAM based objects like 'TempOrder' but ONLY
       when using Local RAM type of sessions. In a distributed environment one can use only 
       pickable types ue to the nature of memcached server.
      """

  id = 'portal_sessions'
  meta_type = 'ERP5 Session Tool'
  portal_type = 'Session Tool'
  allowed_types = ()
  security = ClassSecurityInfo()

  def __getitem__(self, key):
    session = self.getSession(key)
    session._updatecontext(self)
    return session

  def getSession(self, session_id, session_duration=None):
    """ Return session object. """
    storage_plugin = self._getStoragePlugin()
    # expire explicitly as each session can have a different life duration
    storage_plugin.expireOldCacheEntries(forceCheck=1)
    session = storage_plugin.get(session_id, SESSION_SCOPE, None)
    if session is None:
      # init it in cache and use different Session types based on cache plugin type used as a storage
      storage_plugin_type = storage_plugin.__class__.__name__
      if storage_plugin_type in ("RamCache",):
        session = RamSession()
      elif storage_plugin_type in ("DistributedRamCache",):
        session = DistributedSession()
        session._updateSessionId(session_id)
      if session_duration is None:
        # set session duration (this is used from backend storage machinery for expire purposes)
        session_duration = self.portal_caches[SESSION_CACHE_FACTORY].objectValues()[0].cache_duration
      session._updateSessionDuration(session_duration)
      storage_plugin.set(session_id, SESSION_SCOPE, session, session_duration)
    else:
      # cache plugin returns wrapper (CacheEntry instance)
      session = session.getValue()
    return session 

  def newContent(self, id, **kw):
    """ Create new session object. """
    session =  self.getSession(id)
    session._updatecontext(self)
    session.update(**kw)
    return session

  security.declareProtected(Permissions.AccessContentsInformation, 'manage_delObjects')
  def manage_delObjects(self, ids=[], REQUEST=None):
    """ Delete session object. """
    storage_plugin = self._getStoragePlugin()
    if not isinstance(ids, list) or isinstance(ids, list):
      ids = [ids]
    for session_id in ids:
      storage_plugin.delete(session_id, SESSION_SCOPE)
 
  def _getStoragePlugin(self):
    """ Get cache storage plugin."""
    global storage_plugin
    storage_plugin = self.portal_caches.getRamCacheRoot()[SESSION_CACHE_FACTORY].getCachePluginList()[0]
    return storage_plugin
