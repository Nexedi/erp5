from Products.ZSQLCatalog.SQLCatalog import ComplexQuery
from Products.ZSQLCatalog.SQLCatalog import Query
"""
  This script creates a list Person objects based
  on the M0 form information. It updates the list of persons
  based on fast input entries.
"""
from string import zfill
global result_list
global uid
uid = 0
result_list = []
request = context.REQUEST
listbox = getattr(request, 'listbox', None) # Retrieve the fast input data if any
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
result_uid = [x.getUid() for x in context.portal_catalog(query=query, **kw)]
result_document = [x.getObject() for x in context.portal_catalog(query=query, **kw)]
display = 'thumbnail'
format = 'jpg'
resolution ='75'
for doc in result_document:
   content_information = doc.getContentInformation()
   page_number = int(content_information.get('Pages', 0))
   page_list = range(page_number)
   page_number_list = []
   for i in page_list:
     url = '%s?display=%s&format=%s&resolution=%s&frame=%s'%(doc.absolute_url(),
                                  display,format,resolution,i)
     new_doc = doc.asContext(thumbnail=url)
     result_list.append(new_doc)
     page_number_list.append(i)

listbox = getattr(result_list, 'listbox', None)
return result_list
