portal = context.getPortalObject()
assignment = context

if assignment.getValidationState() != 'open':
  # No need to create anything in such case
  # Skip
  return

search_kw = {}
for category in assignment.getCategoryList():
  base_category, _ = category.split('/', 1)
  search_kw['strict__%s__uid' % base_category] = assignment.getValueUidList(base_category)
search_kw['strict__destination_decision__uid'] = assignment.getParentValue().getUid()

assignment_request = portal.portal_catalog.getResultValue(
  portal_type='Assignment Request',
  simulation_state=['submitted', 'validated', 'suspended'],
  **search_kw
)
if assignment_request is not None:
  return

assignment_request = portal.assignment_request_module.newContent(
  portal_type='Assignment Request',
  title=assignment.getTitle(),
  category_list=assignment.getCategoryList(),
  activate_kw=activate_kw
)
assert assignment_request.getDestinationDecision(None) is None, assignment_request.getDestinationDecision(None)
assignment_request.edit(
  destination_decision_value=assignment.getParentValue(),
  activate_kw=activate_kw
)

assignment_request.submit()
assignment_request.validate()
return assignment_request
