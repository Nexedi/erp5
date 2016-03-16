'''
  return the list of the file attached to the declaration where title is in request_income_title_list
'''

request_outcome_title_list = []
sub_object_list = [x.getObject() for x in context.searchFolder(validation_state=['draft','embedded'])]
return [x for x in sub_object_list if x.getTitle() in request_outcome_title_list]
