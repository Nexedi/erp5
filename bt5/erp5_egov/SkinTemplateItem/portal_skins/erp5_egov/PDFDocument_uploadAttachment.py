request = context.REQUEST

from Products.CMFCore.utils import getToolByName
translateString = context.Base_translateString

result, mode = context.Base_edit('PDFDocument_viewAttachmentReportSection', silent_mode=1, field_prefix='your_')

bad_file = ""
if mode == 'edit':
  (kw, encapsulated_editor_list) = result
  if not same_type(kw['attachment_title'], []):
    attachment_title_list = []
    attachment_file_list = []
    attachment_title_list.append(kw['attachment_title'])
    attachment_file_list.append(kw['attachment'])
  else:
    attachment_title_list = kw['attachment_title']
    attachment_file_list = kw['attachment']

  attachment_list = zip(attachment_file_list, attachment_title_list)

  attachment_count = 0
  type_dict = {}
  type_allowed_content_type_list = context.getTypeInfo().getTypeAllowedContentTypeList()
  for i in range(len(attachment_list)+1)[1:]:
    type = getattr(context.getTypeInfo(), "getAttachmentModel%s" % i, None)
    title = getattr(context.getTypeInfo(), "getAttachmentTitle%s" % i, None) 
    if title is not None and title() is not None and type is not None and type() is not None:
      type_object = context.restrictedTraverse(context.getPortalObject().getUrl()+"/portal_types/"+type())
      type_dict[title()] =  type_object.getId()
      if type_object.getId() not in type_allowed_content_type_list: 
        type_allowed_content_type_list.append(type_object.getId())
  context.getTypeInfo().setTypeAllowedContentTypeList(type_allowed_content_type_list)
  # use hidden_content_type_list to hide action Add on interfaces (like Add File) 
  context.getTypeInfo().setTypeHiddenContentTypeList(type_allowed_content_type_list)

  # XXX make sure it is a list
  for attachment, title in attachment_list:
    if attachment:
      portal = context.getPortalObject()
      attachment_portal_type =  context.EGov_guessPortalType(attachment)
      if attachment_portal_type is not None and attachment_portal_type==type_dict[title]:
          document_new_content_kw = {
            'file': attachment,
            'portl_type':type_dict[title],
            'container_path':context.getUrl(),
            'file_name':attachment.filename,
          }
          attachment_count += 1
          container = getToolByName(portal, 'portal_contributions', None)
          document = container.newContent(**document_new_content_kw)
          document_edit_kw = {
            'title': title,
          }
          document.edit(**document_edit_kw)
      else:
          bad_file = "%s '%s' must be %s file"  % (bad_file, attachment.filename, type_dict[title])        

portal_status_message = ""
if attachment_count or bad_file:
  if attachment_count:
    portal_status_message = translateString("Added ${attachment_count} attachment(s) to the current form.",
                             mapping = dict(attachment_count=attachment_count))
  if bad_file:
    portal_status_message = translateString("${portal_status_message} ${bad_file}",
                             mapping = dict(portal_status_message=portal_status_message , bad_file=bad_file)) 
else: 
  portal_status_message = translateString("No attachment was added. Please select a file to add an attachment.")

return context.Base_redirect(form_id, keep_items = dict(portal_status_message =portal_status_message), **kw)
