"""
  This script is a proxy wrapper to get worklist information.
  XXX: To be extended to return more than role.
"""

portal_workflow = context.getPortalObject().portal_workflow
workflow = getattr(portal_workflow, workflow_id)
worklist = getattr(workflow.worklists, worklist_id)
roles = worklist.getGuard().getRolesText().split(';')
return roles
