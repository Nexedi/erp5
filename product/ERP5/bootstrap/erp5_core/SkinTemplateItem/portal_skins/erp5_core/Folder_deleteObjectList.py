if uids is None:
  uids = []
if listbox_uid is None:
  listbox_uid = []
request=context.REQUEST
portal = context.getPortalObject()
Base_translateString = portal.Base_translateString

portal.portal_selections.updateSelectionCheckedUidList(selection_name,listbox_uid,uids)
uids = portal.portal_selections.getSelectionCheckedUidsFor(selection_name)

if uids == []:
  message = Base_translateString("Please select one or more items to delete first.")
  qs = '?portal_status_message=%s' % message
  return request.RESPONSE.redirect( context.absolute_url() + '/' + form_id + qs )

field_id='listbox'
field_selection_name='folder_delete_selection'
# XXX If we come from the view mode -> list mode proxy, make sure we don't make
# another proxy to this proxy.
if form_id == 'Base_viewListModeRenderer':
  form_id = context.Base_viewListModeRenderer.listbox.get_value('form_id')
  field_id = context.Base_viewListModeRenderer.listbox.get_value('field_id')
  field_selection_name = context.Base_viewListModeRenderer.listbox.get_value('selection_name')

kw = {'uid': uids, 'form_id': form_id, 'field_id': field_id}
request.set('object_uid', context.getUid())
request.set('uids', uids)
request.set('proxy_form_id', form_id)
request.set('proxy_field_id', field_id)
request.set('proxy_field_selection_name', field_selection_name)
request.set('ignore_hide_rows', 1)

portal.portal_selections.setSelectionParamsFor('folder_delete_selection', kw)
return context.Folder_viewDeleteDialog(uids=uids, REQUEST=request)
