## Script (Python) "base_folder_delete"
##title=Delete objects from a folder
##parameters=selection_index=None,form_id='',uids=None,ids=None,form_from=None

request=context.REQUEST
selection_index=None

#return uids

#request.set('uid',uids)
#request.set('reset',1)
#request.set('portal_type','Tissu')

kw = {'uid': uids}
request.set('object_uid', context.getUid())
context.portal_selections.setSelectionParamsFor('folder_delete_selection', kw)
return context.folder_delete_view(REQUEST=request, uid=uids)