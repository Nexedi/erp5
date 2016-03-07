gap_id_cache = context.REQUEST.other.get('Movement_getNodeGapIdCache', {})
key = brain.node_relative_url
gap_id = gap_id_cache.get(key)
if gap_id is None:
  gap_id = context.getPortalObject().restrictedTraverse(
                    key).Account_getGapId()
  gap_id_cache[key] = gap_id
  context.REQUEST.other['Movement_getNodeGapIdCache'] = gap_id_cache
return gap_id
