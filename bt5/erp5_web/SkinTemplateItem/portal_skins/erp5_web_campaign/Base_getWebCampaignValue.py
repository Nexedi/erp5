from DateTime import DateTime

if (context.getPortalType() not in context.getPortalDocumentTypeList()) or getattr(context.REQUEST, 'is_web_section_default_document', False):
  # web section is linked directly with web campaign by causality
  web_section = context.getWebSectionValue()
  web_campaign_list = web_section.getCausalityRelatedValueList(portal_type='Web Campaign')
else:
  # search predicate
  tmp_context = context.asContext()
  tmp_context.edit(
    specify_document_reference=context.getReference(),
    start_date=DateTime()
  )
  web_campaign_list = context.portal_domains.searchPredicateList(
    context = tmp_context,
    portal_type = 'Web Campaign',
  )

if web_campaign_list:
  web_campaign_list.sort(key=lambda x:x.getStartDateRangeMin(), reverse=True)
  if batch:
    return web_campaign_list
  return web_campaign_list[0]
