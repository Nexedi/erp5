"""Delete object - this script is called as the last frontier thus its result
gets printed into response body.

The code is a modified version of Folder_delete. We split into two files not to
further complicate the mentioned script.
"""

from Products.ERP5Type.Errors import UnsupportedWorkflowMethod

portal = context.getPortalObject()
translate = portal.Base_translateString

if context.isDeletable(check_relation=True):
  parent = context.getParentValue()
  try:
    history_dict = context.Base_getWorkflowHistory()
    history_dict.pop('edit_workflow', None)
    if history_dict == {} or context.aq_parent.portal_type == 'Preference':
      # Objects that have no workflow history and
      # templates inside preference will be unconditionnaly physically deleted
      parent.manage_delObjects(ids=[context.getId()])
    else:
      # If a workflow manage a history,
      # object should not be removed, but only put in state deleted
      # No need to check if the action is possible,
      # isDeletable would return False in other case
      portal.portal_workflow.doActionFor(context, 'delete_action')
    # redirect back to the container since the context was deleted
    return parent.Base_redirect(
      keep_items={
        "portal_status_message": translate("Document deleted")
      })

  except UnsupportedWorkflowMethod:
    pass

request = portal.REQUEST
request.RESPONSE.setStatus(400)
return context.Base_renderForm(
  dialog_id,
  keep_items={
    'portal_status_message': translate("You are not authorised to delete the document"),
    'portal_status_level': 'warning'
  }
)
