"""Script to remove Documents inside a Folder.

The new UI does not make any exceptions and treat this script as a generic Dialog Form Method.
Thus it receives form_id of previous form, dialog_id of current dialog and uids of objects from
previous Listbox.

The distinction between XHTML resp. RSJS interface is that in the later, this script receives
`uids` directly whether in XHTML it is given `selection_name` and must extract the uids from
the selection.

:param form_id: {str} Form ID of the previous View's FormBox
:param dialog_id: {str} current dialog's Form ID
:param uids: {list[int]} list of "selected" uids from the previous View (only in JS UI)
:param selection_name: {str} if present then user is using XHTML UI
"""
from ZODB.POSException import ConflictError
from Products.CMFCore.WorkflowCore import WorkflowException

portal = context.getPortalObject()
Base_translateString = portal.Base_translateString
translate = Base_translateString
REQUEST = kwargs.get("REQUEST", None) or portal.REQUEST

if selection_name:
  listbox_uid = portal.portal_selections.getSelectionCheckedUidsFor(selection_name)
  if portal.portal_selections.selectionHasChanged(md5_object_uid_list, listbox_uid):
    return context.Base_redirect(keep_items={'portal_status_message': translate("Sorry, your selection has changed.")})

if not listbox_uid:
  return context.Base_redirect(keep_items={
    'portal_status_message': translate("Please select one or more items first."),
    'portal_status_level': "warning"})


if True:
  # already filters out documents with relations that cannot be deleted
  object_list = context.Folder_getDeleteObjectList(uid=listbox_uid)
  object_not_deletable_len = len(listbox_uid) - len(object_list)

  # some documents cannot be deleted thus we stop and warn the user
  if object_not_deletable_len == 1:
    return context.Base_redirect(keep_items={
      'portal_status_message': translate("Sorry, 1 item is in use."),
      'portal_status_level': "warning"})
  elif object_not_deletable_len > 1:
    return context.Base_redirect(keep_items={
      'portal_status_message': translate("Sorry, ${count} items are in use.", mapping={'count': str(object_not_deletable_len)}),
      'portal_status_level': "warning"})

  if True:

    # Do not delete objects which have a workflow history    
    object_to_remove_list = []
    object_to_delete_list = []

    for obj in object_list:

      history_dict = obj.Base_getWorkflowHistory()
      history_dict.pop('edit_workflow', None)
      if history_dict == {} or obj.aq_parent.portal_type=='Preference':
        # templates inside preference will be unconditionnaly physically
        # deleted
        object_to_remove_list.append(obj)
      else:
        # If a workflow manage a history, 
        # object should not be removed, but only put in state deleted
        object_to_delete_list.append(obj)

    # Remove some objects
    try:
      if object_to_remove_list:
        if context.portal_type == 'Preference':
          # Templates inside preference are not indexed, so we cannot pass
          # uids= to manage_delObjects and have to use ids=
          context.manage_delObjects(
                        ids=[x.getId() for x in object_to_remove_list],
                        REQUEST=REQUEST)
          portal.portal_caches.clearCacheFactory('erp5_ui_medium')
        else:
          context.manage_delObjects(
                        uids=[x.getUid() for x in object_to_remove_list],
                        REQUEST=REQUEST)
    except ConflictError:
      raise
    except Exception as error:
      return context.Base_renderMessage(str(error), "error")
    else: # in the case of no exception raised report sucess
      object_ids = [x.getId() for x in object_to_remove_list]
      comment = Base_translateString('Deleted objects: ${object_ids}',
                                     mapping={'object_ids': object_ids})
      try:
        # record object deletion in workflow history
        portal.portal_workflow.doActionFor(context, 'edit_action',
                                           comment=comment)
      except WorkflowException:
        # no 'edit_action' transition for this container
        pass

      message = Base_translateString("Deleted.")

      # Try to call "delete_action" workflow transition on documents which defined it
      # Failure of such a call is not a failure globally. The document was deleted anyway
      for obj in object_to_delete_list:
        # Hidden transition (without a message displayed)
        # are not returned by getActionsFor
        try:
          portal.portal_workflow.doActionFor(obj, 'delete_action')
        except ConflictError:
          raise
        except Exception:
          pass

    # make sure nothing is checked after
    if selection_name:
      portal.portal_selections.setSelectionCheckedUidsFor(selection_name, ())

return context.Base_redirect(form_id, keep_items={"portal_status_message": str(message)})
