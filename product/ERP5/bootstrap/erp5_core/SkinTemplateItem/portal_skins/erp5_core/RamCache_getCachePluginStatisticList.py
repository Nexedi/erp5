"""
This script will dynamically get cache statistics information and 
format it so it can be used in a listbox field.
"""
from Products.ERP5Type.Document import newTempBase

# get all cache statistics 
portal = context.getPortalObject()
cache_stats = portal.portal_caches.getCacheTotalMemorySize()
cache_factory_list_stats = cache_stats['stats']
cache_factory_id = context.getParentValue().getId()
if cache_factory_id not in cache_factory_list_stats:
  # If this cache factory is not in the stats, it means we have to
  # update cache structure. XXX Probably an interaction should do this instead.
  portal.portal_caches.updateCache()
cache_plugin_stats = cache_factory_list_stats[cache_factory_id]
cache_plugin_stats_data = cache_plugin_stats['cp_cache_keys_total_size']

if statistics_criteria == 'total':
  # return just mrmotu usage for cache plugin
  return cache_plugin_stats['total']

result = []
counter = 0
for cache_key,cache_key_memory in cache_plugin_stats_data.items():
  obj = newTempBase(context, 
                    'temp_translation_%d' %counter,
                    cache_key = cache_key,
                    cache_key_memory = cache_key_memory)
  obj.setUid('new_%d' %counter)
  counter += 1
  result.append(obj)

# sort result
if kw.get('sort_on', None) is not None:
  sort_on_attr, sort_on_order = kw['sort_on'][0]
  result.sort(key=lambda x: int(getattr(x, sort_on_attr)))
  if sort_on_order == 'descending':
    result.reverse()

return result
