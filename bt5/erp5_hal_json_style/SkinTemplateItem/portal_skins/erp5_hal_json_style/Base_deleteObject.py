from ZODB.POSException import ConflictError
from Products.CMFCore.WorkflowCore import WorkflowException

"""
some duplicated code with Folder_delete instead of modify Folder_delete
intended to make code easy understanding 
"""

portal = context.getPortalObject()
Base_translateString = portal.Base_translateString
REQUEST = portal.REQUEST

history_dict = context.Base_getWorkflowHistory()
history_dict.pop('edit_workflow', None)

if history_dict == {} or context.aq_parent.portal_type == 'Preference':
  try:
    if context.portal_type == 'Preference':
    # Templates inside preference are not indexed, so we cannot pass
    # uids= to manage_delObjects and have to use ids=
      context.manage_delObjects(
        ids= [context.getId()],
             REQUEST=REQUEST)
      portal.portal_caches.clearCacheFactory('erp5_ui_medium')
    else:
      context.manage_delObjects(
        uids= [context.getUid()],
        REQUEST=REQUEST)
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
