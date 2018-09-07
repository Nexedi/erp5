"""Returns the worklists queries for ticket workflow, as a mapping where the key is the worklist ID and the value a JIO query.

This script has proxy role, as only manager can access workflow configuration.
"""
from Products.ERP5Type.Message import translateString
portal = context.getPortalObject()

query_dict = {}

workflow = portal.portal_workflow.ticket_workflow
workflow_state_var = workflow.variables.getStateVar()

for worklist in workflow.worklists.objectValues():
  query_list = [{
    'type': 'complex',
    'operator': 'OR',
    'query_list': [
      {'key': 'local_roles',
       'type': 'simple',
       'value': role, } for role in worklist.getGuard().getRolesText().split("; ")]
  }]

  for key in worklist.getVarMatchKeys():
    value = worklist.getVarMatch(key)
    if key == workflow_state_var:
      # instead of having {'validation_state': 'draft'}, we want to have
      #  {'translated_validation_state_title': 'Brouillon'}
      # so that it looks good in the module view.
      key = 'translated_%s_title' % key
      state_title = workflow['states'].restrictedTraverse(value).title_or_id()
      value = unicode(translateString(
        '%s [state in %s]' % (state_title, workflow.getId()),
        default=unicode(translateString(state_title))))

    query_list.append({
      'key': key,
      'value': value,
      'type': 'simple',
    })

  query_dict[worklist.getId()] = {
    'type': 'complex',
    'query_list': query_list
  }

return query_dict
