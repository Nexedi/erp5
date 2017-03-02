portal = context.getPortalObject()

event_list = []
person = portal.portal_membership.getAuthenticatedMember().getUserValue()

if person is not None:
  # XXX Wrong way to filter the same person in source OR destination.
  event_list.extend(portal.event_module.searchFolder(source_relative_url=person.getRelativeUrl(), **kw))
  event_list.extend(portal.event_module.searchFolder(destination_relative_url=person.getRelativeUrl(), **kw))
  return event_list

return portal.event_module.searchFolder(**kw)
