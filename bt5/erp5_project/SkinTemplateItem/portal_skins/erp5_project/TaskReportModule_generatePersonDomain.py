domain_list = []

if depth == 0:
  task_uid_list  = context.portal_selections.getSelectionUidList(context=context, selection_name='task_report_module_selection')
  person_result = context.portal_catalog(portal_type=["Person",],
                                         source_related_uid=task_uid_list,
                                         select_list=['portal_type', 'relative_url', 'id', 'title'],
                                         sort_on = (('title','ascending'),))
  person_dict = {}
  person_list = []
  append = person_list.append
  for person in person_result:
    key = person.uid
    if key not in person_dict:
      person_dict[key] = None
      category_dict = {'relative_url':person.relative_url,
                       'portal_type': "Person",
                       'id':person.id,
                       'title':person.title,
                       'uid':person.uid}
      append(category_dict)
else:
  return domain_list

for person in person_list:
  domain = parent.generateTempDomain(id = 'sub' + person['id'] )
  domain.edit(title = person['title'],
              membership_criterion_base_category = ('source', ),
              membership_criterion_category = (person['relative_url'],),
              domain_generator_method_id = script.id,
              uid = person['uid'])

  domain_list.append(domain)

return domain_list
