cache_id = '{}.cache'.format(script.getId())

financial_section_cache = context.REQUEST.other.get(cache_id, {})
key = brain.node_relative_url
financial_section_title = financial_section_cache.get(key)
if financial_section_title is None:
  financial_section_title = context.getPortalObject().restrictedTraverse(
      key).getFinancialSectionTranslatedTitle()
  financial_section_cache[key] = financial_section_title
  context.REQUEST.other[cache_id] = financial_section_cache
return financial_section_title
