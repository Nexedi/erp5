# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
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

from __future__ import absolute_import
import string
from contextlib import contextmanager
from time import time
from AccessControl import allow_class, ClassSecurityInfo
from Acquisition import aq_base
from BTrees.Length import Length
from .CachePlugins.BaseCache import CachedMethodError
from persistent import Persistent
from zLOG import LOG, WARNING
from Products.ERP5Type import Permissions
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from Products.ERP5Type.Utils import simple_decorator
from warnings import warn

DEFAULT_CACHE_SCOPE = 'GLOBAL'
DEFAULT_CACHE_FACTORY = 'erp5_ui_short'
is_cache_initialized = False


def initializePortalCachingProperties(self):
  """ Init CachingMethod properties."""
  ## check if global CachingMethod is initialized in RAM for this ERP5 site. If not init it
  global is_cache_initialized
  if not is_cache_initialized:
    portal_caches = getattr(self.getPortalObject(), 'portal_caches', None)
    if portal_caches is None:
      return
    # we set is_cache_initialized right now to prevent infinite loops
    is_cache_initialized = True
    ## update cache structure from portal_caches
    try:
      portal_caches.updateCache()
    except AttributeError:
      is_cache_initialized = False
      return


class ZODBCookie(Persistent):

  value = 0

  def __getstate__(self):
    return self.value

  def __setstate__(self, value):
    self.value = value

  def _p_resolveConflict(self, old_state, saved_state, new_state):
    return 1 + max(saved_state, new_state)

  def _p_independent(self):
    return 1


class CacheCookieMixin:
  """Provides methods managing (ZODB) persistent keys to access caches
  """
  security = ClassSecurityInfo()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getCacheCookie')
  def getCacheCookie(self, cache_name='default'):
    """Get key of valid cache for this object"""
    cache_name = '_cache_cookie_' + cache_name
    try:
      return self.__dict__[cache_name].value
    except KeyError:
      setattr(self, cache_name, ZODBCookie())
      return ZODBCookie.value

  security.declareProtected(Permissions.ModifyPortalContent, 'newCacheCookie')
  def newCacheCookie(self, cache_name):
    """Invalidate cache for this object"""
    cache_name = '_cache_cookie_' + cache_name
    try:
      self.__dict__[cache_name].value += 1
    except KeyError:
      setattr(self, cache_name, ZODBCookie())


class CacheFactory:
  """ CacheFactory is a RAM based object which contains different cache plugin
  objects ordered in a list.
  """

  cache_plugins = []
  cache_duration = 180

  def __init__(self, cache_plugins, cache_params):
    self.cache_plugins = cache_plugins
    self.cache_duration = cache_params.get('cache_duration')

    ## separete local and shared cache plugins
    self.quick_cache = self.cache_plugins[0]
    self._quick_cache_get = self.quick_cache.get
    try:
      self.shared_caches = self.cache_plugins[1:]
    except IndexError:
      self.shared_caches = []

    ## set 'check_expire_cache_interval' to the minimal value between
    ## individual 'check_expire_cache_interval' for each cache plugin contained
    l = []
    for cp in self.cache_plugins:
      l.append(cp.cache_expire_check_interval)
    l = [x for x in l if x is not None and x != 0]
    self.cache_expire_check_interval = min(l)
    self._next_cache_expire_check_at = time() + self.cache_expire_check_interval

  def __call__(self, callable_object, cache_id, scope, cache_duration=None, *args, **kwd):
    """ When CacheFactory is called it will try to return cached value using
    appropriate cache plugin.
    """
    ## Expired Cache (if needed)
    now = time()
    if now > self._next_cache_expire_check_at:
      self.expire(now)

    try:
      return self._quick_cache_get(cache_id, scope).getValue()
    except KeyError:
      ## not in local, check if it's in shared
      for shared_cache in self.shared_caches:
        try:
          cache_entry = shared_cache.get(cache_id, scope)
        except KeyError:
          pass
        else:
          value = cache_entry.getValue()
          ## update local cache
          self.quick_cache.set(cache_id, scope, value,
                              cache_duration,
                              cache_entry.calculation_time)
          return value

    cache_duration = self.cache_duration
    ## not in any available cache plugins calculate and set to local ..
    start = time()
    value = callable_object(*args, **kwd)
    end = time()
    calculation_time = end - start
    self.quick_cache.set(cache_id, scope, value, cache_duration, calculation_time)

    ## .. and update rest of caches in chain except already updated local one
    for shared_cache in self.shared_caches:
      shared_cache.set(cache_id, scope, value, cache_duration, calculation_time)
    return value

  def expire(self, now):
    """ Expire cache plugins """
    self._next_cache_expire_check_at = now + self.cache_expire_check_interval
    for cache_plugin in self.getCachePluginList():
      cache_plugin.expireOldCacheEntries()

  def getCachePluginList(self, omit_cache_plugin_name=None):
    """ get list of all cache plugins except specified by name in omit """
    rl = []
    for cp in self.cache_plugins:
      if omit_cache_plugin_name != cp.__class__.__name__:
        rl.append(cp)
    return rl

  def getCachePluginByClassName(self, cache_plugin_name):
    """ get cache plugin by its class name """
    for cp in self.cache_plugins:
      if cache_plugin_name == cp.__class__.__name__:
        return cp
    return None

  def getCachePluginById(self, id, default=None):
    """ get cache plugin by its id """
    for cp in self.cache_plugins:
      if id == cp.id:
        return cp
    if default is not None:
      return default
    raise KeyError("No such plugin exists %s" % id)


  def clearCache(self):
    """ clear cache for this cache factory """
    for cp in self.cache_plugins:
      cp.clearCache()

class CachingMethod:
  """CachingMethod is a RAM based global Zope class which contains different
  CacheFactory objects for every available ERP5 site instance.
  """

  ## cache factories will be initialized for every ERP5 site
  factories = {}

  def _default_cache_id_generator(method_id, *args, **kw):
    """ Generate proper cache id based on *args and **kw  """
    ## generate cache id out of arguments passed.
    ## depending on arguments we may have different
    ## cache_id for same method_id
    return str((method_id, args, sorted(kw.items())))

  @staticmethod
  def erasable_cache_id_generator(method_id, obj, *args, **kw):
    return str((method_id, obj.getCacheCookie(method_id), args, sorted(kw.items())))

  def __init__(self, callable_object, id, cache_duration=180,
               cache_factory=DEFAULT_CACHE_FACTORY,
               cache_id_generator=_default_cache_id_generator):
    """Wrap a callable object in a caching method.

    callable_object must be callable.
    id is used to identify what call should be treated as the same call.
    cache_duration is an old argument kept for backwards compatibility.
    cache_duration is specified per cache factory.
    cache_factory is the id of the cache_factory to use.
    """
    if not callable(callable_object):
      raise CachedMethodError("callable_object %r is not callable"
                              % (callable_object,))
    if not id:
      raise CachedMethodError("id must be specified")
    self.id = id
    self.callable_object = callable_object
    self.cache_duration = cache_duration
    self.cache_factory = cache_factory
    self.generateCacheId = cache_id_generator

  def __call__(self, *args, **kwd):
    """Call the method or return cached value using appropriate cache plugin """

    ## cache scope is based on user which is a kwd argument
    scope = kwd.pop('scope', DEFAULT_CACHE_SCOPE)

    ## generate unique cache id
    cache_id = self.generateCacheId(self.id, *args, **kwd)

    try:
      ## try to get value from cache in a try block
      ## which is faster than checking for keys
      # It is very important to take the factories dictionnary
      # on CachingMethod instead of self, we want a global variable
      cache_factory = CachingMethod.factories[self.cache_factory]
    except KeyError:
      # No cache factory ready, execute without cache. This happens during
      # initialisation
      value = self.callable_object(*args, **kwd)
    else:
      value = cache_factory(
              self.callable_object, cache_id, scope, self.cache_duration,
              *args, **kwd)
    return value

  def delete(self, *args, **kwd):
    """ Delete cache key.
    accept same arguments as __call__ to clear
    the cache entry with the same cache_id
    """
    cache_factory = self.cache_factory
    scope = kwd.pop('scope', DEFAULT_CACHE_SCOPE)
    cache_id = self.generateCacheId(self.id, *args, **kwd)
    cache_factory = CachingMethod.factories[cache_factory]
    for cp in cache_factory.getCachePluginList():
      cp.delete(cache_id, scope)

allow_class(CachingMethod)

# TransactionCache is a cache per transaction. The purpose of this cache is
# to accelerate some heavy read-only operations. Note that this must not be
# enabled when a transaction may modify ZODB objects.
def getReadOnlyTransactionCache():
  """Get the transaction cache.
  """
  return getTransactionalVariable().get('read_only_transaction_cache')

@contextmanager
def readOnlyTransactionCache():
  tv = getTransactionalVariable()
  if 'read_only_transaction_cache' in tv:
    yield
  else:
    tv['read_only_transaction_cache'] = {}
    try:
      yield
    finally:
      del tv['read_only_transaction_cache']

########################################################
## Old global cache functions                         ##
## TODO: Check if it make sense to keep them any more ##
########################################################

def clearCache(cache_factory_list=(DEFAULT_CACHE_FACTORY,)):
  """Clear specified cache factory list."""
  warn("Global function clearCache() is deprecated. Use"
       " portal_caches.clearCache() instead.", DeprecationWarning,
       stacklevel=2)
  cache_storage = CachingMethod.factories
  for cf_key in cache_factory_list:
    if cf_key in cache_storage:
      for cp in cache_storage[cf_key].getCachePluginList():
        cp.clearCache()

def generateCacheIdWithoutFirstArg(method_id, *args, **kwd):
  # If we use CachingMethod as a class method, the first item of args
  # is 'self' that can be ignored to create a cache id.
  return str((method_id, args[1:], kwd))

def caching_instance_method(*args, **kw):
  kw.setdefault('cache_id_generator', generateCacheIdWithoutFirstArg)
  @simple_decorator
  def decorator(function):
    # The speed of returned function must be fast
    # so we instanciate CachingMethod now.
    caching_method = CachingMethod(function, *args, **kw)
    # Here, we can't return caching_method directly because an instanciated
    # class with a __call__ method does not behave exactly like a simple
    # function: if the decorator is used to create a method, the instance on
    # which the method is called would not be passed as first parameter.
    return lambda *args, **kw: caching_method(*args, **kw)
  return decorator

_default_key_method = lambda *args: args
def transactional_cached(key_method=_default_key_method):
  @simple_decorator
  def decorator(function):
    # Unfornately, we can only check functions (not other callable like class).
    assert (key_method is not _default_key_method or
            not getattr(function, '__defaults__', None)), (
      "default 'key_method' of 'transactional_cached' does not work with"
      " functions having default values for parameters")
    key = repr(function)
    def wrapper(*args, **kw):
      cache = getTransactionalVariable().setdefault(key, {})
      subkey = key_method(*args, **kw)
      try:
        return cache[subkey]
      except KeyError:
        cache[subkey] = result = function(*args, **kw)
        return result
    return wrapper
  return decorator
