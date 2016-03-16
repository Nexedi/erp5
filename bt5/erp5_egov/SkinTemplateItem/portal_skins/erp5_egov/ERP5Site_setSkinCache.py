cache_manager_id = 'http_cache'
result = []

def setCache(skin):
  for o in skin.objectValues():
    id = o.id
    if callable(id): id = id()
    if o.meta_type in ('Image', 'File') or id.endswith('.css') or id.endswith('.js'):
      o.ZCacheable_setManagerId(cache_manager_id)
      result.append(id)
    elif o.meta_type == 'Folder':
      setCache(o)

for skin in context.portal_skins.objectValues():
  setCache(skin)

return "\n".join(result)
