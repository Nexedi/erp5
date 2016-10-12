request = context.REQUEST

memcached_tool = context.getPortalObject().portal_memcached.getMemcachedDict(key_prefix=roomid,
                                                              plugin_path='portal_memcached/default_memcached_plugin')

peer_array = []
try:
  peer_array = memcached_tool['peer_names']
except KeyError:
  memcached_tool['peer_names'] = []

if peer_array is None:
  memcached_tool['peer_names'] = []

peer_array.append(peerid)
memcached_tool[peerid] = data;
memcached_tool['peer_names'] = peer_array

request.response.setBody("ok")
return request.response
