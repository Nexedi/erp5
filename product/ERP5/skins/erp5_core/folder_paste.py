## Script (Python) "folder_paste"
##title=Paste objects to a folder from the clipboard
##parameters=form_id
REQUEST=context.REQUEST
if context.cb_dataValid:
  new_item_list = context.manage_pasteObjects(REQUEST['__cp'])
  new_id_list = map(lambda i: i['new_id'],new_item_list)
  for my_id in new_id_list:
    context[my_id].flushActivity(invoke=0, method_id='immediateReindexObject')
    context[my_id].recursiveImmediateReindexObject()
  return REQUEST.RESPONSE.redirect(context.absolute_url() + '/' + form_id + '?portal_status_message=Item(s)+Pasted.')
else:
  return REQUEST.RESPONSE.redirect(context.absolute_url() + '/' + form_id + '?portal_status_message=Copy+or+cut+one+or+more+items+to+paste+first.')
