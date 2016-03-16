from ZODB.POSException import ConflictError
from Products.CMFCore.WorkflowCore import WorkflowException

portal = context.getPortalObject()
Base_translateString = portal.Base_translateString
REQUEST = portal.REQUEST

uids = portal.portal_selections.getSelectionCheckedUidsFor(selection_name)
if portal.portal_selections.selectionHasChanged(md5_object_uid_list, uids):
  message = Base_translateString("Sorry, your selection has changed.")
elif uids:
  # Check if there is some related objets.
  object_list = [x.getObject() for x in context.Folder_getDeleteObjectList(uid=uids)]
  object_used = sum([x.getRelationCountForDeletion() and 1 for x in object_list])

  if object_used > 0:
    if object_used == 1:
      message = Base_translateString("Sorry, 1 item is in use.")
    else:
      message = Base_translateString("Sorry, ${count} items are in use.",
                                     mapping={'count': repr(object_used)})
  else:

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
    except Exception, message:
      pass
    else:
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

      # Change workflow state of others objects
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

      # Generate message
      if not_deleted_count == 1:
        message = Base_translateString("Sorry, you can not delete ${count} item.",
                                       mapping={'count': not_deleted_count})
      elif not_deleted_count > 1:
        message = Base_translateString("Sorry, you can not delete ${count} items.",
                                       mapping={'count': not_deleted_count})
      qs = '?portal_status_message=%s' % message

    # make sure nothing is checked after
    portal.portal_selections.setSelectionCheckedUidsFor(selection_name, ())
else:
  message = Base_translateString("Please select one or more items first.")

return context.Base_redirect(form_id, keep_items={"portal_status_message":message})
