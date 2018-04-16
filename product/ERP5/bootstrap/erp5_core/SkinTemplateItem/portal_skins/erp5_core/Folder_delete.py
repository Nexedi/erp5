"""Script to remove Documents inside a Folder.

The new UI does not make any exceptions and treat this script as a generic Dialog Form Method.
Thus it receives form_id of previous form, dialog_id of current dialog and uid of objects from
previous Listbox.

:param fixit: {int} set to 1 if this action displayed warning/error and the user resubmits
"""
from ZODB.POSException import ConflictError
from Products.CMFCore.WorkflowCore import WorkflowException

portal = context.getPortalObject()
Base_translateString = portal.Base_translateString
translate = Base_translateString
REQUEST = portal.REQUEST
try:
  fixit = int(fixit)
except ValueError:
  fixit = 0

if selection_name:
  uids = portal.portal_selections.getSelectionCheckedUidsFor(selection_name)
  if portal.portal_selections.selectionHasChanged(md5_object_uid_list, uids):
    return context.Base_redirect(keep_items={'portal_status_message': translate("Sorry, your selection has changed.")})

if not uids:
  return context.Base_redirect(keep_items={
    'portal_status_message': translate("Please select one or more items first."),
    'portal_status_level': "warning"})


if True:  # useless indentation
  # check if selected documents contain related objects because we
  # cannot delete those
  search_result = context.Folder_getDeleteObjectList(uid=uids)
  object_list = [x.getObject() for x in context.Folder_getDeleteObjectList(uid=uids)]
  object_list_len = len(object_list)
  object_used_list = [x for x in object_list if x.getRelationCountForDeletion() > 0]
  object_used_list_len = len(object_used_list)
  if not fixit and object_used_list_len > 0:
    if selection_name:
      # if we have selection_name then we work with old-style Selections
      for x in object_used_list:
        uids.remove(x.getUid())
      portal.portal_selections.setSelectionCheckedUidsFor(selection_name, uids)
      return context.Base_renderForm(dialog_id,
        Base_translateString("Unselecting ${count} out of ${total} documents with relations because they cannot be deleted.",
                             mapping={"count": object_used_list_len, 'total': object_list_len}),
        level='warning'
      )
    else:
      # No selection_name means we are in non-XHTML interface thus notify user that re-submission
      # will trigger delete and omit the undeletable documents
      # if user re-confirms we receive fixit=1 flag
      return context.Base_renderForm(dialog_id,
        Base_translateString('Cannot delete ${count} out of ${total} documents because of related documents. Click "Delete" again to omit them and delete the rest.',
                             mapping={"count": object_used_list_len, 'total': object_list_len}),
        level='warning',
        keep_items={'fixit': 1}
      )

  if fixit and object_used_list_len > 0:
    # the user re-submitted the dialog after seeing an error thus remove objects with relations and delete the rest
    for x in object_used_list:
      uids.remove(x.getUid())
    object_list = [x.getObject() for x in context.Folder_getDeleteObjectList(uid=uids)]

  if True:  # useless indentation adding cyclomatic complexity

    # Do not delete objects which have a workflow history    
    object_to_remove_list = []
    object_to_delete_list = []

    for object in object_list:

      history_dict = object.Base_getWorkflowHistory()
      history_dict.pop('edit_workflow', None)
      if history_dict == {} or object.aq_parent.portal_type=='Preference':
        # templates inside preference will be unconditionnaly physically
        # deleted
        object_to_remove_list.append(object)
      else:
        # If a workflow manage a history, 
        # object should not be removed, but only put in state deleted
        object_to_delete_list.append(object)

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
      not_deleted_count = 0
      for object in object_to_delete_list:
        # Hidden transition (without a message displayed)
        # are not returned by getActionsFor
        try:
          portal.portal_workflow.doActionFor(object, 'delete_action')
        except ConflictError:
          raise
        except:
          not_deleted_count += 1

    # make sure nothing is checked after
    if selection_name:
      portal.portal_selections.setSelectionCheckedUidsFor(selection_name, ())

return context.Base_redirect(form_id, keep_items={"portal_status_message": str(message)})
