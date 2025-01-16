quality_element = state_change['object']

previous_one = quality_element.getFollowUpValue(portal_type=quality_element.getPortalType())
if previous_one and previous_one.getValidationState() != 'archived':
  previous_one.archive()
