from DateTime import DateTime

if (context.getPortalType() not in context.getPortalDocumentTypeList()) or getattr(context.REQUEST, 'is_web_section_default_document', False):
  tmp_context = context.getWebSectionValue().asContext()
else:
  tmp_context = context.asContext()

tmp_context.edit(
  start_date=DateTime()
)

web_campaign_list = context.portal_domains.searchPredicateList(
  context = tmp_context,
  portal_type = 'Web Campaign',
  sort_key_method = lambda x:x.getStartDateRangeMin()
)

if web_campaign_list:
  if batch:
    return web_campaign_list
  # get the newest one
  return web_campaign_list[-1]
