"""Returns the workflow states titles for ticket workflow, keyed by state id.

This script has proxy role, as only manager can access workflow configuration.
"""
import six
from Products.ERP5Type.Message import translateString
portal = context.getPortalObject()

info = {}

workflow = portal.portal_workflow.ticket_workflow

for state in workflow.getStateValueList():
  state_title = state.title_or_id()
  state_title = six.text_type(translateString(
      '%s [state in %s]' % (state_title, workflow.getId()),
      default=six.text_type(translateString(state_title))))
  info[state.getReference()] = state_title

return info
