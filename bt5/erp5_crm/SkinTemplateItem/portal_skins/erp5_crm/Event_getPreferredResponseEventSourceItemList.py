"""Returns the possible senders to choose from when creating a response event.

"""
item_list = [ ('', ''),
              (context.getDestinationTitle(), context.getDestination()) ]

logged_in_user = context.getPortalObject().portal_membership.getAuthenticatedMember().getUserValue()
if logged_in_user is not None and logged_in_user.getRelativeUrl() != context.getDestination():
  item_list.append((logged_in_user.getTitle(), logged_in_user.getRelativeUrl()))

return item_list
