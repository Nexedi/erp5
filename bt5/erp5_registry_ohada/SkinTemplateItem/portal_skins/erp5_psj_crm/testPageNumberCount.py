from Products.ZSQLCatalog.SQLCatalog import ComplexQuery
from Products.ZSQLCatalog.SQLCatalog import Query

# Get the list of parent messages
attachment_pdf_list=[]
current_object = context.getObject()
event_list = current_object.getFollowUpRelatedValueList()
attachment_list =[x.getAggregateValueList() for x in event_list]
for y in attachment_list:
 attachment_pdf_list.extend(filter(lambda x:(x.getPortalType()=='PDF'),y))
event_uid_list = map(lambda x: x.getUid(), event_list)
attachment_pdf_uid_list =[x.getUid() for x in attachment_pdf_list]

if not event_uid_list:
 return []

# Build query
query = ComplexQuery(Query(parent_uid=event_uid_list),
                     Query(uid=event_uid_list),
                     Query(parent_uid=attachment_pdf_uid_list),
                     Query(uid=attachment_pdf_uid_list),
                     logical_operator="OR")

kw['portal_type'] = ('PDF')

result_document =[x.getObject() for x in context.portal_catalog(query=query, **kw)]
for x in result_document:
  content_information = x.getContentInformation()
  page_number = int(content_information.get('Pages', 0))
  return [[page_number]]
