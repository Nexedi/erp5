# this script allow to assign attachments to a form
portal = context.getPortalObject()
current_object = context.getObject()
m0_module = context.getPortalObject().m0_module
report_number = current_object.getReportNumber()
form_list = [x.getObject() for x in portal.portal_catalog(portal_type=['M0','M2','M4','P0','P2','P4'],
                      source_reference=report_number)]

for form in form_list:
  if form.getPortalType()=='P0' or form.getPortalType()=='P2' or form.getPortalType()=='P4':
    form.setTitle(form.getFirstName() +' ' +form.getLastName())
    form.edit(follow_up_value=current_object)
  elif form.getPortalType()=='P2' or form.getPortalType()=='P4':
    form.setTitle(form.getOwnerFirstName() +' ' +form.getOwnerLastName())
    form.edit(follow_up_value=current_object)
  else:
    form.edit(follow_up_value=current_object)
  group_list = current_object.getGroupList()
  function_list = current_object.getFunctionList()
  site_list = current_object.getSiteList()
  classification = current_object.getClassification()
  publication_section_list = current_object.getPublicationSectionList()
  owner = current_object.getSourceValue()

# Build metadata dict
  metadata = {}
  if group_list: metadata['group_list'] = group_list
  if function_list: metadata['function_list'] = function_list
  if site_list: metadata['site_list'] = site_list 
  if classification: metadata['classification'] = classification 
  if publication_section_list: metadata['publication_section_list'] = publication_section_list

# Ingest attachments
  for attachment_item in current_object.getAttachmentInformationList():
  # We do not care about files without name
    file_name = attachment_item.get('file_name')
  # We do not take into account the message itself
  # XXX - this implementation is not acceptable in
  # the long term. Better approach to defining the
  # body of a message is required
    if file_name and not file_name.startswith('part'):
      index = attachment_item['index']
      data = current_object.getAttachmentData(index)
      if attachment_item['file_name'].endswith('pdf'):
        portal_type = 'PDF'
      elif attachment_item['file_name'].endswith('jpg'):
        portal_type = 'Image'
      else:
        portal_type = 'File'
    # XXX - too bad we are not using content_type here
      d = form.newContent(data=data, source_reference=file_name,portal_type=portal_type)
      current_object.setAggregateList(context.getAggregateList() + [d.getRelativeUrl()])
  current_object.edit(follow_up_value= form)
if form_list:
  current_object.assignToForm()
return current_object.EmailDocument_viewAttachmentListRenderer()
