request = context.REQUEST
domain_list = []

if depth == 0:
  preferred_group = context.portal_preferences.getPreferredSectionCategory()
  if preferred_group:

    person_sql_list = context.portal_catalog(
      portal_type='Person', group_relative_url=preferred_group)

    for person in person_sql_list:
      person = person.getObject()
      domain = parent.generateTempDomain(id='sub%s' % person.getId())
      domain.edit(title = person.getTitle(),
                  membership_criterion_base_category = ('source', ), 
                  membership_criterion_category = ('source/%s' % person.getRelativeUrl(),),
                  domain_generator_method_id = script.id,
                  uid = person.getUid())
                    
      domain_list.append(domain)

return domain_list
