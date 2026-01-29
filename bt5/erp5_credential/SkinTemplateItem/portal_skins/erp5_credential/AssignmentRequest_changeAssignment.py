assignment_request = context
portal = context.getPortalObject()
assignment = None
person = assignment_request.getDestinationDecisionValue(portal_type='Person')

if person is None:
  raise ValueError('No person document found')

search_kw = {}
for category in assignment_request.getCategoryList():
  base_category, _ = category.split('/', 1)
  search_kw['strict__%s__uid' % base_category] = assignment_request.getValueUidList(base_category)
search_kw.pop('strict__destination_decision__uid')

assignment_list = portal.portal_catalog(
  portal_type='Assignment',
  parent_uid=person.getUid(),
  validation_state='open',
  **search_kw
)

assignment_request_state = assignment_request.getSimulationState()
if assignment_request_state == 'submitted':
  if 0 < len(assignment_list):
    assignment_request.validate(comment='Assignment already exists (%s).' % assignment_list[0].getRelativeUrl())
    assignment_request.invalidate(comment='Assignment already exists (%s).' % assignment_list[0].getRelativeUrl())
  else:
    category_list = [x for x in assignment_request.getCategoryList() if not x.startswith('destination_decision/')]
    assignment = person.newContent(
      portal_type='Assignment',
      title=assignment_request.getTitle(),
      category_list=category_list,
      activate_kw=activate_kw
    )
    assignment.open(comment='Assignment created by %s.' % assignment_request.getRelativeUrl())
    # create a new assignment for the user
    assignment_request.validate(comment='Assignment created (%s).' % assignment.getRelativeUrl())

elif assignment_request_state == 'validated':
  if 0 == len(assignment_list):
    # Assignment was probably manually closed
    assignment_request.suspend(comment='No matching assignment found.')
    assignment_request.invalidate(comment='No matching assignment found.')

elif assignment_request_state == 'suspended':
  for assignment in assignment_list:
    assignment.close('Closed by the assignment request (%s)' % assignment_request.getRelativeUrl())
  assignment_request.invalidate(comment='Assignment closed.')

assignment_request.reindexObject(activate_kw=activate_kw)
return assignment
