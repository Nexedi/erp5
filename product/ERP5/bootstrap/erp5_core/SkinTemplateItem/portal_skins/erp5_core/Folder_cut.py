portal = context.getPortalObject()
Base_translateString = portal.Base_translateString

context.portal_selections.updateSelectionCheckedUidList(selection_name,listbox_uid,uids)
uids = context.portal_selections.getSelectionCheckedUidsFor(selection_name)
# make sure nothing is checked after
context.portal_selections.setSelectionCheckedUidsFor(selection_name, [])
request=context.REQUEST



if uids != []:
  # Check if there is some related objets.
  object_used = 0

  object_list = [x.getObject() for x in context.portal_catalog(uid=uids)]
  object_used = sum([x.getRelationCountForDeletion() for x in object_list])

  if object_used > 0:
    if object_used == 1:
      message = Base_translateString("Sorry, 1 item is in use.")
    else:
      message = Base_translateString("Sorry, ${count} items are in use.",
                                     mapping={'count': repr(object_used)})
  else:
    context.manage_cutObjects(uids=uids, REQUEST=request)
    message = Base_translateString("Items cut.")
else:
  message = Base_translateString("Please select one or more items to cut first.")

return context.Base_redirect(form_id, keep_items=dict(portal_status_message=message))
