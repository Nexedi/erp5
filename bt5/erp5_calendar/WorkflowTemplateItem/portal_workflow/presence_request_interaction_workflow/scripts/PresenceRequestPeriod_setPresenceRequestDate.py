presence_request = state_change['object'].getParentValue()
presence_request_period_list = presence_request.objectValues(
  portal_type='Presence Request Period',
)
presence_request.setStartDate(
  min([x.getStartDate() for x in presence_request_period_list])
)
presence_request.setStopDate(
  max([x.getStopDate() for x in presence_request_period_list])
)
