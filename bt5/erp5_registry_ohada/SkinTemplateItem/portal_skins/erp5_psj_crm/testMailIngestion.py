"""
  This script is invoked at the end of ingestion process.
  The default behaviour is to receive messages so that they
  are marked as 'New' and appear in the worklist.
"""

group_list = context.getGroupList()
function_list = context.getFunctionList()
site_list = context.getSiteList()
classification = context.getClassification()
publication_section_list = context.getPublicationSectionList()
owner = context.getSourceValue()

# Build metadata dict
metadata = {}
if group_list: metadata['group_list'] = group_list
if function_list: metadata['function_list'] = function_list
if site_list: metadata['site_list'] = site_list 
if classification: metadata['classification'] = classification 
if publication_section_list: metadata['publication_section_list'] = publication_section_list

contribution_tool = context.getPortalObject().portal_contributions

# Ingest attachments
for attachment_item in context.getAttachmentInformationList():
  # We do not care about files without name
  file_name = attachment_item.get('file_name')
  # We do not take into account the message itself
  # XXX - this implementation is not acceptable in
  # the long term. Better approach to defining the
  # body of a message is required
  if file_name and not file_name.startswith('part'):
    index = attachment_item['index']
    data = context.getAttachmentData(index)
    # XXX - too bad we are not using content_type here
    d = contribution_tool.newContent(data=data, file_name=file_name, **metadata)
    context.setAggregateList(context.getAggregateList() + [d.getRelativeUrl()])

return context.EmailDocument_viewAttachmentListRenderer()
