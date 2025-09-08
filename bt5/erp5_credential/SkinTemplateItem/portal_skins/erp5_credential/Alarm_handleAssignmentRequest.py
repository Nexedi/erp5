portal = context.getPortalObject()

if not portal.portal_preferences.getPreferredAssignmentRequestAlarmAutomaticCall():
  return

activate_kw = {'tag': tag}

portal.portal_catalog.searchAndActivate(
  portal_type='Assignment Request',
  simulation_state=['submitted', 'suspended'],

  method_id='AssignmentRequest_changeAssignment',
  method_kw={'activate_kw': activate_kw},
  activate_kw=activate_kw
)

context.activate(after_tag=tag).getId()
