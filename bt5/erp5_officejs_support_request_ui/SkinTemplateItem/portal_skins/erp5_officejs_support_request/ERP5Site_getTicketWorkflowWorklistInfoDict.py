"""Returns the worklists queries for ticket workflow, as a mapping where the key is the worklist ID and the value a JIO query.

If `portal_type` is provided, only return worklists that apply for this portal type.

This script has proxy role, as only manager can access workflow configuration.
"""
from Products.ERP5Type.Message import translateString
import six
portal = context.getPortalObject()

query_dict = {}

workflow = portal.portal_workflow.ticket_workflow
workflow_state_var = workflow.getStateVariable()

for worklist in workflow.getWorklistValueList():
  identity_criterion_dict = worklist.getIdentityCriterionDict()
  if portal_type \
       and 'portal_type' in worklist.getCriterionPropertyList() \
       and portal_type not in identity_criterion_dict.get('portal_type'):
    continue

  query_list = []
  for key, value in six.iteritems(identity_criterion_dict):
    if key == workflow_state_var:
      # instead of having {'validation_state': 'draft'}, we want to have
      #  {'translated_validation_state_title': 'Brouillon'}
      # so that it looks good in the module view.
      key = 'translated_%s_title' % key
      state_title = workflow.getStateValueByReference(value[0]).title_or_id()
      value = unicode(translateString(
        '%s [state in %s]' % (state_title, workflow.getId()),
        default=unicode(translateString(state_title))))

    if isinstance(value, (tuple, list)):
      query_list.extend([{
        'type': 'complex',
        'operator': 'OR',
        'query_list': [{'key': key,
                       'type': 'simple',
                       'value': v, } for v in value]
      }])
    else:
      query_list.append({
        'key': key,
        'value': value,
        'type': 'simple',
      })

  query_dict[worklist.getReference()] = {
    'type': 'complex',
    'query_list': query_list
  }

return query_dict
