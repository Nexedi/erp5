request = context.REQUEST

memcached_tool = context.getPortalObject().portal_memcached.getMemcachedDict(key_prefix=roomid,
                                                              plugin_path='portal_memcached/default_memcached_plugin')
data = memcached_tool[name]

return data
