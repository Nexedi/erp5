portal = context.getPortalObject()

if not portal.portal_preferences.getPreferredAssignmentRequestAlarmAutomaticCall():
  return


# This alarm browse all objects, and so is slow
# Do not block other activities
activate_kw = {'tag': tag, 'priority': 5}
context.activate(after_tag=tag).getId()

# Do not trigger the activities if it seems there are enough Assignment Requests
# This should prevent to spawn those, except during the first migration
# or if an admin manually create an Assignment
assignment_count = portal.portal_catalog.countResults(
  portal_type='Assignment',
  validation_state=['open']
)[0][0]
assignment_request_count_list = portal.portal_catalog(
  portal_type='Assignment Request',
  simulation_state=['submitted', 'validated', 'suspended'],
  select_list=['COUNT(*)'],
  group_by_list=['portal_type', 'simulation_state']
)
submitted_count = 0
validated_count = 0
suspended_count = 0
for sql_result in assignment_request_count_list:
  if sql_result.getSimulationState() == 'submitted':
    submitted_count = sql_result['COUNT(*)']
  elif sql_result.getSimulationState() == 'validated':
    validated_count = sql_result['COUNT(*)']
  elif sql_result.getSimulationState() == 'suspended':
    suspended_count = sql_result['COUNT(*)']

if (submitted_count + validated_count + suspended_count) < assignment_count:
  # No enough assignment request.
  # Try to create them
  portal.portal_catalog.searchAndActivate(
    portal_type='Assignment',
    validation_state=['open'],

    method_id='Assignment_createMissingAssignmentRequest',
    method_kw={'activate_kw': activate_kw},
    activate_kw=activate_kw
  )

elif assignment_count < validated_count:
  # Too many assignment requests
  # Check if user manually closed the assignment
  portal.portal_catalog.searchAndActivate(
    portal_type='Assignment Request',
    simulation_state='validated',

    method_id='AssignmentRequest_changeAssignment',
    method_kw={'activate_kw': activate_kw},
    activate_kw=activate_kw
  )
