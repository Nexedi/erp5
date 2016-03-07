movement_list = []
organisation = context

for person in organisation.getSubordinationRelatedValueList(portal_type='Person',
                                                            checked_permission="View"):
  movement_list.extend(person.Person_getTaskMovementHistoryList(**kw))

return movement_list
