## Script (Python) "Folder_delete"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id='',selection_index=None,object_uid=None,selection_name=None,field_id=None,uids=None,cancel_url='',listbox_uid=[],md5_object_uid_list=''
##title=Delete objects from a folder
##
selected_uids = context.portal_selections.updateSelectionCheckedUidList(selection_name,listbox_uid,uids)
uids = context.portal_selections.getSelectionCheckedUidsFor(selection_name)

error = context.portal_selections.selectionHasChanged(md5_object_uid_list,uids)

#return uids

REQUEST=context.REQUEST
#REQUEST.set('uids',uids)
qs = ''
ret_url = ''

ret_url = context.absolute_url() + '/' + form_id
if error:
  qs = '?portal_status_message=Sorry+your+selection+has+changed'
elif uids is not None:
  context.manage_delObjects(uids=uids, REQUEST=REQUEST)
  qs = '?portal_status_message=Deleted.'
else:
  qs = '?portal_status_message=Please+select+one+or+more+items+first.'

return REQUEST.RESPONSE.redirect( ret_url + qs )
