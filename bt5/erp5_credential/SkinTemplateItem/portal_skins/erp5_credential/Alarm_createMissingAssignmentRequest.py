portal = context.getPortalObject()

if not portal.portal_preferences.getPreferredAssignmentRequestAlarmAutomaticCall():
  return

# Do not trigger the activities if it seems there are enough Assignment Requests
# This should prevent to spawn those, except during the first migration
# or if an admin manually create an Assignment
assignment_count = portal.portal_catalog.countResults(
  portal_type='Assignment',
  validation_state=['open']
)[0][0]
assignment_request_count = portal.portal_catalog.countResults(
  portal_type='Assignment Request',
  simulation_state=['submitted', 'validated', 'suspended']
)[0][0]
#raise NotImplementedError('%s %s' % (assignment_count, assignment_request_count))

if assignment_count <= assignment_request_count:
  return

activate_kw = {'tag': tag}

portal.portal_catalog.searchAndActivate(
  portal_type='Assignment',
  validation_state=['open'],

  method_id='Assignment_createMissingAssignmentRequest',
  method_kw={'activate_kw': activate_kw},
  activate_kw=activate_kw
)

context.activate(after_tag=tag).getId()
