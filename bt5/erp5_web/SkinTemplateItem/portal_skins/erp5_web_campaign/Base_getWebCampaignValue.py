from DateTime import DateTime

now = DateTime()

if (context.getPortalType() not in context.getPortalDocumentTypeList()) or getattr(context.REQUEST, 'is_web_section_default_document', False):
  web_section = context.getWebSectionValue()
  tmp_context = web_section.asContext(categories = ['display_domain/specify_document'])
  tmp_context.edit(
    specify_document=context.getRelativeUrl(),
    start_date=now
  )
else:
  tmp_context = context.asContext(categories= ['display_domain/specify_document', 'display_domain/web_content'] +
                                  context.getPublicationSectionList(base=True) +
                                  context.getFollowUpList(base=True))
  tmp_context.edit(
    specify_document=context.getReference(),
    start_date=now
  )

web_campaign_list = context.portal_domains.searchPredicateList(
  context = tmp_context,
  portal_type = 'Web Campaign',
  sort_key_method = lambda x:x.getStartDateRangeMin(),
)

if web_campaign_list:
  if batch:
    return web_campaign_list
  # get the newest one
  return web_campaign_list[-1]
