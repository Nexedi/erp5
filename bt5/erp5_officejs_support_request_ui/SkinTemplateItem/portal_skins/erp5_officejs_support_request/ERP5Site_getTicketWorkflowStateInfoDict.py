"""Returns the workflow states titles for ticket workflow, keyed by state id.

This script has proxy role, as only manager can access workflow configuration.
"""
from Products.ERP5Type.Message import translateString
portal = context.getPortalObject()

info = {}

workflow = portal.portal_workflow.ticket_workflow

for state in workflow['states'].objectValues():
  state_title = state.title_or_id()
  if 0:
    # We don't translate yet, it needs several other fixes
    # see https://lab.nexedi.com/nexedi/erp5/merge_requests/778
    state_title = unicode(translateString(
      '%s [state in %s]' % (state_title, workflow.getId()),
      default=unicode(translateString(state_title))))
  info[state.getId()] = state_title

return info
