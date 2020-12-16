# By default, there are three cache_managers, http_cache and anonymous_http_cache and user_ram_cache.
cache_manager_id = 'http_cache'
result = []

def setCache(skin):
  for o in skin.objectValues():
    id_ = o.id
    if callable(id_): id_ = id_()
    if o.meta_type in ('Image', 'File', 'Filesystem Image', 'Filesystem File') or id_.endswith('.css') or id_.endswith('.js'):
      if o.ZCacheable_getManagerId() != cache_manager_id:
        o.ZCacheable_setManagerId(cache_manager_id)
        result.append(o.absolute_url(relative=1))
    elif o.meta_type == 'Folder':
      setCache(o)

for skin in context.portal_skins.objectValues():
  setCache(skin)

return "\n".join(result)
