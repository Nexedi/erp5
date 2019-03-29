# Retrieve the edit action
"""
  Special edit method which returns to view mode.
  The view_document_url is used to define the URL to return to
  after editing the document.
"""

from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.CMFCore.utils import getToolByName

request=context.REQUEST

message = ''

# add the attachments :
translateString = context.Base_translateString

if form_id == 'view':
  result, mode = context.asContext(edit=context.edit,
            **{form_id: context.getTypeInfo().getERP5Form()}
          ).Base_edit('PDFDocument_viewAttachmentReportSection', silent_mode=1, field_prefix='your_')
else:
  result, mode = context.Base_edit('PDFDocument_viewAttachmentReportSection', silent_mode=1, field_prefix='your_')


attachment_count = 0

bad_file = ""
if mode == 'edit':
  (kw, encapsulated_editor_list) = result
  if 'attachment_title' in kw.keys():
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
      if title is not None and type is not None:
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

message = ""
if attachment_count or bad_file:
  if attachment_count:
    message = translateString("Added ${attachment_count} attachment(s) to the current form.",
                             mapping = dict(attachment_count=attachment_count))
  if bad_file:
    message = translateString("${portal_status_message} ${bad_file}",
                             mapping = dict(portal_status_message=message , bad_file=bad_file)) 
else:
  if form_id != 'view' and context.PDFDocument_getRequirementCount() != 0: 
    message = translateString("Please add ${missing_file} missing file(s) to continue.", 
                             mapping = dict(missing_file=context.PDFDocument_getRequirementCount())) 



next_url_dict = {
   'view':'PDFDocument_viewAttachmentList',
}

# edit the document with the entered data before to change of state

if form_id == 'view':
  base_edit_result = context.PDFDocument_edit(form_id=form_id, 
                  selection_index=selection_index, 
                  selection_name=selection_name, 
                  dialog_id=dialog_id, 
                  ignore_layout=ignore_layout, 
                  editable_mode=editable_mode, 
                  silent_mode=silent_mode, 
                  field_prefix=field_prefix)

# if there is somme errors (like required field not filled),
# return to the same page, and display Base_edit error message
if request.get('field_errors', ''):
  return base_edit_result

if form_id != 'view' and context.PDFDocument_getRequirementCount() != 0:
  return request['RESPONSE'].redirect(
             "%s/%s?portal_status_message=%s" %
             (context.absolute_url(), form_id, message))


if not next_url_dict.has_key(form_id):
  next_url = 'PDFDocument_viewLoginInformation'
  # if the next url is PDFDocument_viewLoginInformation, submit the application

  if context.getTypeInfo().getStepPrepayment():
    submit_action = 'pending_action'
  else:
    submit_action = 'submit_draft_action'
  try : 
    message=""
    context.portal_workflow.doActionFor(context,
                                      submit_action)
  except ValidationFailed as message: 
    context.pdb()
    return request['RESPONSE'].redirect(
               "%s/%s?portal_status_message=%s" %
               (context.absolute_url(), form_id, message))
  #context.submit()
else:
  next_url = next_url_dict[form_id]

return context.Base_redirect(next_url, keep_items = dict(portal_status_message=message), **kw)
