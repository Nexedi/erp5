request = context.REQUEST

memcached_tool = context.getPortalObject().portal_memcached.getMemcachedDict(key_prefix=roomid,
                                                              plugin_path='portal_memcached/default_memcached_plugin')
del memcached_tool[name];
peer_names = memcached_tool["peer_names"]
peer_names.remove(name)
memcached_tool["peer_names"] = peer_names

return "done"
