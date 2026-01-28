assignment_request = context
person = assignment_request.getDestinationDecisionValue(portal_type='Person')
person_before_migration = assignment_request.getDestinationValue()

error_list = []

if person is None:
  if person_before_migration is None:
    return ['Error: Neither Destination and Destination Decision is set.']
  if person_before_migration.getPortalType() != 'Person':
    return ['Error: Cannot invoke migration because destination isnt a person.']
  error_list.append('Assignment has destination_decision not migrated yet to destination')
  if fixit:
    assignment_request.edit(
      destination_decision_value=person_before_migration,
      destination=None)
    assert not assignment_request.getDestination()

return error_list
