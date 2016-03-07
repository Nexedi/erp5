return context.Ticket_getResourceItemList(
  portal_type='Event',
  use_relative_url=context.getPortalObject().portal_preferences.getPreferredEventResponseUse())
