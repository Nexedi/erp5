portal = context.getPortalObject()
Base_translateString = portal.Base_translateString

context.portal_selections.updateSelectionCheckedUidList(selection_name, listbox_uid,uids)
uids = context.portal_selections.getSelectionCheckedUidsFor(selection_name)
# make sure nothing is checked after
context.portal_selections.setSelectionCheckedUidsFor(selection_name, [])

request=context.REQUEST

if uids != []:
  context.manage_copyObjects(uids=uids, REQUEST=request, RESPONSE=request.RESPONSE)
  message = Base_translateString("Items copied.")
else:
  message = Base_translateString("Please select one or more items to copy first.")

return context.Base_redirect(form_id,
             keep_items=dict(portal_status_message=message))
