request = context.REQUEST

memcached_tool = context.getPortalObject().portal_memcached.getMemcachedDict(key_prefix=roomid,
                                                             plugin_path='portal_memcached/default_memcached_plugin')

try:
  peer_array = memcached_tool['peer_names']
except KeyError:
  peer_array = []

return peer_array
