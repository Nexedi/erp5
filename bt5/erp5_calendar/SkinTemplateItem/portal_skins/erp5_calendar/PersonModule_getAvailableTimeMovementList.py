result_list = []

for person in context.portal_selections.getSelectionValueList(context=context, REQUEST=context.REQUEST,
                                                              selection_name='person_module_selection'):
  result_list.extend(person.Person_getAvailableTimeMovementList(**kw))

return result_list
