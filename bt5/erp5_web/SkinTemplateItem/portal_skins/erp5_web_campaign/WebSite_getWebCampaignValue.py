from DateTime import DateTime
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery, ComplexQuery

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
  query = None

else:
  publication_section_list = context.getPublicationSectionList()
  follow_up_list = context.getFollowUpList()
  display_domain_list = ['web_content', 'specify_page']
  # specify page 's reference can't be indexed in predicate table
  # thus use query to find specified web campaign
  query = ComplexQuery(SimpleQuery(causality_reference=context.getReference()),
                       SimpleQuery(display_domain_relative_url='display_domain/web_content'),
                       logical_operator='OR')



# now find if has web campaign match predicate
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
  query = query,
  tested_base_category_list = tested_base_category_list
)
# check if has specified web campaign
if len(web_campaign_list) > 1:
  specified_web_campaign_list = []
  common_web_campaign_list =  []
  specified_web_campaign_reference_list = []
  for web_campaign in web_campaign_list:
    if web_campaign.getCausality():
      specified_web_campaign_list.append(web_campaign)
      specified_web_campaign_reference_list.append(web_campaign.getCausalityReference())
    else:
      common_web_campaign_list.append(web_campaign)

  if context.getReference() in specified_web_campaign_reference_list:
    if len(specified_web_campaign_list) == 1:
      return specified_web_campaign_list[0]
    context.log('Multiple web campaign found: %s' % [x.getRelativeUrl() for x in specified_web_campaign_list])
  else:
    if len(common_web_campaign_list) == 1:
      return common_web_campaign_list[0]
    context.log('Multiple web campaign found: %s' % [x.getRelativeUrl() for x in common_web_campaign_list])

  if batch:
    return web_campaign_list
  return


if len(web_campaign_list) == 1:
  return web_campaign_list[0]
