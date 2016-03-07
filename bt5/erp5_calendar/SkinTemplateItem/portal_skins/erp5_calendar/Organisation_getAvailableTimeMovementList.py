result_list = []

for person in context.getSubordinationRelatedValueList(portal_type='Person',
                                                       checked_permission="View"):
  result_list.extend(person.Person_getAvailableTimeMovementList(**kw))

return result_list
