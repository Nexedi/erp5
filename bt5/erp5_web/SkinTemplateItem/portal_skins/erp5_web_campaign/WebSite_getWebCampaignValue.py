from DateTime import DateTime

now = DateTime()
tested_base_category_list = []
web_section = context.getWebSectionValue()

tmp_context = context.portal_trash.newContent(
  portal_type='Web Campaign',
  temp_object=1,
  start_date=now
)

# default document may don't have any setting
# we check web section's predicate instead
if (context.getPortalType() not in context.getPortalDocumentTypeList()) or getattr(context.REQUEST, 'is_web_section_default_document', False):
  criterion_category_list = web_section.getMembershipCriterionCategoryList()
  publication_section_list = [x.split('/', 1)[-1] for x in criterion_category_list if x.startswith('publication_section/')]
  follow_up_list = [x.split('/', 1)[-1] for x in criterion_category_list if x.startswith('follow_up/')]
  display_domain_list = ['web_section']

else:
  publication_section_list = context.getPublicationSectionList()
  follow_up_list = context.getFollowUpList()
  display_domain_list = ['web_content']


if publication_section_list:
  tested_base_category_list.append('publication_section')
  tmp_context.edit(publication_section_list = publication_section_list)

if follow_up_list:
  tested_base_category_list.append('follow_up')
  tmp_context.edit(follow_up_list = follow_up_list)

if not tested_base_category_list:
  return

tested_base_category_list.append('display_domain')
tmp_context.edit(
  display_domain_list = display_domain_list
)

web_campaign_list = context.portal_domains.searchPredicateList(
  context = tmp_context,
  portal_type = 'Web Campaign',
  tested_base_category_list = tested_base_category_list
)
# check now if has delicated web campaign
if len(web_campaign_list) > 1:
  delicated_web_campaign_list = []
  common_web_campaign_list =  []
  delicated_web_campaign_reference_list = []
  for web_campaign in web_campaign_list:
    if web_campaign.getCausality():
      delicated_web_campaign_list.append(web_campaign)
      delicated_web_campaign_reference_list += web_campaign.WebCampaign_getRelatedDocumentReferenceList(causality=True)
    else:
      common_web_campaign_list.append(web_campaign)

  if context.getReference() in delicated_web_campaign_reference_list:
    if len(delicated_web_campaign_list) == 1:
      return delicated_web_campaign_list[0]
    context.log('Multiple web campaign found: %s' % [x.getRelativeUrl() for x in delicated_web_campaign_list])
  else:
    if len(common_web_campaign_list) == 1:
      return common_web_campaign_list[0]
    context.log('Multiple web campaign found: %s' % [x.getRelativeUrl() for x in common_web_campaign_list])

  if batch:
    return web_campaign_list
  return


if len(web_campaign_list) == 1:
  delicated_reference_list = web_campaign_list[0].WebCampaign_getRelatedDocumentReferenceList(causality=True)
  if (not delicated_reference_list) or (context.getReference() in delicated_reference_list):
    return web_campaign_list[0]
