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


from six import string_types as basestring
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Acquisition import aq_base
from six.moves import UserDict
import six
# pylint:disable=import-error,no-name-in-module
if six.PY3:
  import collections.abc as collections_abc
else:
  import collections as collections_abc
# pylint:enable=import-error,no-name-in-module


# the ERP5 cache factory used as a storage
SESSION_CACHE_FACTORY = 'erp5_session_cache'
SESSION_SCOPE = 'SESSION'

# =24 hours, really last default duration value set if not defined in storage
DEFAULT_SESSION_DURATION = 86400

_marker=[]

# global storage plugin
storage_plugin = None


def remove_acquisition_wrapper(obj):
  if isinstance(obj, basestring):
    return obj
  obj = aq_base(obj)
  if isinstance(obj, collections_abc.Mapping):
    return obj.__class__({
        remove_acquisition_wrapper(k): remove_acquisition_wrapper(v)
        for k, v in obj.items()})
  if isinstance(obj, (collections_abc.Sequence, collections_abc.Set)):
    return obj.__class__([remove_acquisition_wrapper(o) for o in obj])
  return obj


def restore_acquisition_wrapper(obj, context):
  if isinstance(obj, basestring):
    return obj
  if hasattr(obj, '__of__'):
    obj = obj.__of__(context)
  if isinstance(obj, collections_abc.Mapping):
    return obj.__class__({
        restore_acquisition_wrapper(k, context): restore_acquisition_wrapper(v, context)
        for k, v in obj.items()})
  if isinstance(obj, (collections_abc.Sequence, collections_abc.Set)):
    return obj.__class__([restore_acquisition_wrapper(o, context) for o in obj])
  return obj


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

  # a handle to current acquisition context
  _aq_context = None

  def __getstate__(self):
    """filter out acquisition wrappers when serializing.
    """
    state = {
        'session_duration': self.session_duration,
        'data': {k: aq_base(v) for k, v in six.iteritems(self.data)}
    }
    if 'session_id' in self.__dict__:
      state['session_id']  = self.session_id
    return state

  def _updatecontext(self, aq_context):
    """ Update current acquisition context. """
    self._aq_context = aq_context

  def __getitem__(self, key):
    if key in self.data:
      # returned it wrapped in acquisition context
      return restore_acquisition_wrapper(self.data[key], self._aq_context)
    raise KeyError(key)

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

  def __setitem__(self, key, item):
    # save value without its acquisition context
    UserDict.__setitem__(self, key, remove_acquisition_wrapper(item))

  def update(self, dict=None, **kwargs):  # pylint: disable=redefined-builtin
    for k, v in six.iteritems((dict or kwargs)):
      # make sure to use our __setitem__ which removes acquistion wrappers
      self[k] = v


class DistributedSession(Session):
  """ Distributed Session dictionary.
      It uses DistributedRamCache plugins."""

  # session_id used to get respective dictionary from memcached
  session_id = None

  def _updateStorage(self):
    """ Update backend storage. """
    assert self.session_id
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

  def update(self, dict=None, **kwargs): # pylint: disable=redefined-builtin
    Session.update(self, dict, **kwargs)
    self._updateStorage()

  def setdefault(self, key, failobj=None):
    r = Session.setdefault(self, key, failobj)
    self._updateStorage()
    return r

  def pop(self, key, *args):
    r = Session.pop(self, key, *args)
    self._updateStorage()
    return r

  def popitem(self):
    r = Session.popitem(self)
    self._updateStorage()
    return r


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
      # will work only for local RAM sessions
      session['shopping_cart'] = context.newContent(portal_type='Order', temp_object=True, id='987654321')
      (you can also use 'session.edit(shopping_cart=context.newContent(context.newContent(portal_type='Order', temp_object=True, id='987654321'))' )

      (later in another script you can acquire shopping_cart):

      session_id = '1234567'
      session = context.portal_sessions[session_id]
      shopping_cart = session['shopping_cart']

      Please note that:
        - developer is responsible for handling an unique session_id (using cookies for example).
        - it's not recommended to store in portal_sessions ZODB persistent objects because in order
      to store them in Local RAM portal_sessions tool will remove acquisition wrapper. At "get"
      request they'll be returned wrapped.
        - developer can store temporary ERP5 documents like 'TempOrder', but keep
      in mind that after making changes to temporary documents they need to be
      saved again in portal_sessions, so:

      >>> shopping_cart = context.newContent(portal_type='Order', temp_object=True, id='987654321')
      >>> shopping_cart.newContent(portal_type='Order Line', quantity=1, resource=...)
      >>> session['shopping_cart'] = shopping_cart

      # modifying a temp document from session is valid
      >>> shopping_cart.getMovementList()[0].setQuantity(3)
      # but the session still reference the documents as it was when saved to session:
      >>> session['shopping_cart'].getMovementList()[0].getQuantity()
      1
      # to make the change persist in the session, the temp document has to be saved again:
      >>> session['shopping_cart'] = shopping_cart
      >>> session['shopping_cart'].getMovementList()[0].getQuantity()
      3

      """

  id = 'portal_sessions'
  meta_type = 'ERP5 Session Tool'
  portal_type = 'Session Tool'
  title = 'Sessions'
  allowed_types = ()
  security = ClassSecurityInfo()

  def __getitem__(self, key):
    session = self.getSession(key)
    session._updatecontext(self)
    return session

  security.declarePrivate('getSession')
  def getSession(self, session_id, session_duration=None):
    """ Return session object. """
    storage_plugin_ = self._getStoragePlugin()
    # expire explicitly as each session can have a different life duration
    storage_plugin_.expireOldCacheEntries(forceCheck=1)
    session = storage_plugin_.get(session_id, SESSION_SCOPE, None)
    if session is None:
      # init it in cache and use different Session types based on cache plugin type used as a storage
      storage_plugin_type = storage_plugin_.__class__.__name__
      if storage_plugin_type in ("RamCache",):
        session = Session()
      elif storage_plugin_type in ("DistributedRamCache",):
        session = DistributedSession()
        session._updateSessionId(session_id)
      if session_duration is None:
        # set session duration (this is used from backend storage machinery for expire purposes)
        cache_plugin = self.portal_caches[SESSION_CACHE_FACTORY].objectValues()[0]
        session_duration = cache_plugin.getCacheDuration()
      session._updateSessionDuration(session_duration)
      storage_plugin_.set(session_id, SESSION_SCOPE, session, session_duration)
    else:
      # cache plugin returns wrapper (CacheEntry instance)
      session = session.getValue()
    return session

  security.declarePublic('newContent')
  def newContent(self, id, **kw): # pylint: disable=redefined-builtin
    """ Create new session object. """
    session =  self.getSession(id)
    session._updatecontext(self)
    session.update(**kw)
    return session

  security.declareProtected(Permissions.AccessContentsInformation, 'manage_delObjects')
  def manage_delObjects(self, ids=(), REQUEST=None, *args, **kw):
    """ Delete session object. """
    storage_plugin_ = self._getStoragePlugin()
    if not isinstance(ids, (list, tuple)):
      ids = [ids]
    for session_id in ids:
      storage_plugin_.delete(session_id, SESSION_SCOPE)

  def _getStoragePlugin(self):
    """ Get cache storage plugin."""
    global storage_plugin # pylint: disable=global-statement
    storage_plugin = self.portal_caches.getRamCacheRoot()[SESSION_CACHE_FACTORY].getCachePluginList()[0]
    return storage_plugin
