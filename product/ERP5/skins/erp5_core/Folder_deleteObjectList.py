## Script (Python) "Folder_deleteObjectList"
##title=Delete objects from a folder
##parameters=selection_index=None,form_id='',uids=[], listbox_uid=[],selection_name=''

request=context.REQUEST

selected_uids = context.portal_selections.updateSelectionCheckedUidList(selection_name,listbox_uid,uids)
uids = context.portal_selections.getSelectionCheckedUidsFor(selection_name)


kw = {'uid': uids}
request.set('object_uid', context.getUid())
request.set('uids', uids)
context.portal_selections.setSelectionParamsFor('folder_delete_selection', kw)
return context.Folder_viewDeleteDialog(uids=uids, REQUEST=request)

