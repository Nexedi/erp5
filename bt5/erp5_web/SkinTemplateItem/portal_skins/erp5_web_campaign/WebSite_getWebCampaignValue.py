from DateTime import DateTime

now = DateTime()

tested_base_category_list = []


web_section = context.getWebSectionValue()

default_document = web_section.getDefaultDocumentValue()

# default document may don't have any setting
# we check web section's predicate instead
if default_document.getUid() == context.getUid() or context.getPortalType() not in context.getPortalDocumentTypeList():
  criterion_category_list = web_section.getMembershipCriterionCategoryList()
  publication_section_list = [x.split('/', 1)[-1] for x in criterion_category_list if x.startswith('publication_section/')]
  follow_up_list = [x.split('/', 1)[-1] for x in criterion_category_list if x.startswith('follow_up/')]

else:
  publication_section_list = context.getPublicationSectionList()
  follow_up_list = context.getFollowUpList()

tmp_context = context.portal_trash.newContent(
  portal_type='Web Campaign',
  temp_object=1,
  start_date=now
)


if publication_section_list:
  tested_base_category_list.append('publication_section')
  tmp_context.edit(publication_section_list = publication_section_list)

if follow_up_list:
  tested_base_category_list.append('follow_up')
  tmp_context.edit(follow_up_list = follow_up_list)

if not tested_base_category_list:
  return


web_campaign_list = context.portal_domains.searchPredicateList(
  context = tmp_context,
  portal_type = 'Web Campaign',
  tested_base_category_list = tested_base_category_list
)

if len(web_campaign_list) > 1:
  context.log('Multiple web campaign found: %s' % [x.getRelativeUrl() for x in web_campaign_list])
  if batch:
    return web_campaign_list

if len(web_campaign_list) == 1:
  return web_campaign_list[0]
