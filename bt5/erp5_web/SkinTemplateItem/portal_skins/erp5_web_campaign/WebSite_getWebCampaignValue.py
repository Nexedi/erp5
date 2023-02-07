from DateTime import DateTime
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery, NegatedQuery, ComplexQuery

now = DateTime()

tested_base_category_list = []

tmp_context = context.portal_trash.newContent(
  portal_type='Web Campaign',
  temp_object=1,
  start_date=now
)
query_list = []
publication_section_list = context.getPublicationSectionList()
follow_up_list = context.getFollowUpList()

if publication_section_list:
  tested_base_category_list.append('publication_section')
  tmp_context.edit(publication_section_list = publication_section_list)
  query_list.append(NegatedQuery(SimpleQuery(publication_section_uid=None)))

if follow_up_list:
  tested_base_category_list.append('follow_up')
  tmp_context.edit(follow_up_list = follow_up_list)
  query_list.append(NegatedQuery(SimpleQuery(follow_up_uid=None)))

if not tested_base_category_list:
  return

query = None
if query_list:
  if len(query_list) == 1:
    query = query_list[0]
  else:
    query = ComplexQuery(query_list[0],
                         query_list[1],
                         logical_operator='AND')

web_campaign_list = context.portal_domains.searchPredicateList(
  context=tmp_context,
  portal_type='Web Campaign',
  query = query,
  tested_base_category_list=tested_base_category_list
)


if len(web_campaign_list) > 1:
  raise ValueError('Multiple web campaign found: %s' % [x.getRelativeUrl() for x in web_campaign_list])

if len(web_campaign_list) == 1:
  return web_campaign_list[0]
