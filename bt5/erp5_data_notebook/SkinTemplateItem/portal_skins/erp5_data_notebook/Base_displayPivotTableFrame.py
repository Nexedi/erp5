memcached_tool = context.getPortalObject().portal_memcached
memcached_dict = memcached_tool.getMemcachedDict(key_prefix='pivottablejs', plugin_path='portal_memcached/default_memcached_plugin')
return memcached_dict[key]
