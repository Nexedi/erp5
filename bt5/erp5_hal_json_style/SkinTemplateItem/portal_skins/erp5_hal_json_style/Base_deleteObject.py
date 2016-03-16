from ZODB.POSException import ConflictError

"""
some duplicated code with Folder_delete instead of modify Folder_delete
intended to make code easy understanding 
"""

portal = context.getPortalObject()

history_dict = context.Base_getWorkflowHistory()
history_dict.pop('edit_workflow', None)

if history_dict == {} or context.getParentValue().portal_type == 'Preference': 
  try:
    context.getParentValue().manage_delObjects(
      ids= [context.getId()])
  except ConflictError:
    raise
  except Exception:
    pass

else:
  try:
    portal.portal_workflow.doActionFor(context, 'delete_action')
  except ConflictError:
    raise
  except:
    pass
