import hashlib
import hmac
from Products.ERP5Type.Cache import DEFAULT_CACHE_SCOPE
import six

CACHE_FACTORY_NAME = 'bearer_token_cache_factory'

def getHMAC(self, key, body):
  # type: (erp5.portal_type.Base, bytes, bytes) -> str
  digest = hmac.new(key, body, digestmod=hashlib.md5)
  return digest.hexdigest()

def _getCacheFactory(self, cache_factory_name):
  portal = self.getPortalObject()
  cache_tool = portal.portal_caches
  cache_factory = cache_tool.getRamCacheRoot().get(cache_factory_name)
  #XXX This conditional statement should be remove as soon as
  #Broadcasting will be enable among all zeo clients.
  #Interaction which update portal_caches should interact with all nodes.
  if cache_factory is None \
      and getattr(cache_tool, cache_factory_name, None) is not None:
    #ram_cache_root is not up to date for current node
    cache_tool.updateCache()
  return cache_tool.getRamCacheRoot().get(cache_factory_name)

def setBearerToken(self, key, body, cache_factory_name=CACHE_FACTORY_NAME):
  # type: (erp5.portal_type.Base, str, Any, str) -> None
  if not isinstance(key, six.string_types):
    __traceback_info__ = key
    raise TypeError("Wrong key type %s" % (type(key)))
  cache_factory = _getCacheFactory(self, cache_factory_name)
  cache_duration = cache_factory.cache_duration
  for cache_plugin in cache_factory.getCachePluginList():
    cache_plugin.set(key, DEFAULT_CACHE_SCOPE,
                     body, cache_duration=cache_duration)

def getBearerToken(self, key, cache_factory_name=CACHE_FACTORY_NAME):
  # type: (erp5.portal_type.Base, str, str) -> Any
  assert isinstance(key, six.string_types)
  cache_factory = _getCacheFactory(self, cache_factory_name)
  for cache_plugin in cache_factory.getCachePluginList():
    cache_entry = cache_plugin.get(key, DEFAULT_CACHE_SCOPE)
    if cache_entry is not None:
      return cache_entry.getValue()
  raise KeyError('Key %r not found' % key)
