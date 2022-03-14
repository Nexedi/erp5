workflow = context.getPortalObject().portal_workflow.restrictedTraverse(
  workflow_id)

return workflow.Base_redirect(
  keep_items={
    "portal_status_message": workflow.getTranslatedTitle()
  })
