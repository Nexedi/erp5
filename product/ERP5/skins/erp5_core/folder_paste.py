## Script (Python) "folder_paste"
##title=Paste objects to a folder from the clipboard
##parameters=form_id
REQUEST=context.REQUEST
error_message = ''
if context.cb_dataValid:
  # We first look if the content of objects to paste is allowed
  # inside this folder
  object_list = context.cb_dataItems()
  portal_type_list = map(lambda x: x.getPortalType(),object_list)
  allowed_type_list = map(lambda x: x.id, context.allowedContentTypes())
  for portal_type in portal_type_list:
    if portal_type not in allowed_type_list:
      error_message = 'Sorry+you+can+not+paste+theses+Items+here'
if context.cb_dataValid and error_message=='':
  new_item_list = context.manage_pasteObjects(REQUEST['__cp'])
  new_id_list = map(lambda i: i['new_id'],new_item_list)
  for my_id in new_id_list:
    context[my_id].flushActivity(invoke=0, method_id='immediateReindexObject')
    context[my_id].recursiveImmediateReindexObject()
  return REQUEST.RESPONSE.redirect(context.absolute_url() + '/' + form_id + '?portal_status_message=Item(s)+Pasted.')
elif context.cb_dataValid and error_message!='':
  return REQUEST.RESPONSE.redirect(context.absolute_url() + '/' + form_id + '?portal_status_message=%s' % error_message)
else:
  return REQUEST.RESPONSE.redirect(context.absolute_url() + '/' + form_id + '?portal_status_message=Copy+or+cut+one+or+more+items+to+paste+first.')
