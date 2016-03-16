# By default, there are three cache_managers, http_cache and anonymous_http_cache and user_ram_cache.
cache_manager_id = 'http_cache'
result = []

def setCache(skin):
  for o in skin.objectValues():
    id = o.id
    if callable(id): id = id()
    if o.meta_type in ('Image', 'File', 'Filesystem Image', 'Filesystem File') or id.endswith('.css') or id.endswith('.js'):
      if o.ZCacheable_getManagerId() != cache_manager_id:
        o.ZCacheable_setManagerId(cache_manager_id)
        result.append(o.absolute_url(relative=1))
    elif o.meta_type == 'Folder':
      setCache(o)

for skin in context.portal_skins.objectValues():
  setCache(skin)

return "\n".join(result)
