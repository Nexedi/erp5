request = context.REQUEST
domain_list = []

closed_state_list = ['draft', 'invalidated', 'suspended']

category_list = []
if depth == 0:
  category_list = [x for x in context.portal_catalog(portal_type='Project',
                                                     validation_state= closed_state_list)]
                                                     #validation_state='validated')]
else:
  parent_object = context.restrictedTraverse(parent.parent_url)
  category_list = parent_object.contentValues(portal_type='Project Line', sort_on='int_index')

for category in category_list:
  domain = parent.generateTempDomain(id='sub%s' % category.getId())

  membership_criterion_category = []
  sub_category_list = [category]
  while sub_category_list:
    sub_category = sub_category_list.pop()
    membership_criterion_category.append('source_project/%s/' % sub_category.getRelativeUrl())
    sub_category_list.extend(sub_category.contentValues(portal_type='Project Line'))

  domain.edit(title = category.getTitle(),
              membership_criterion_base_category = ('source_project', ),
              membership_criterion_category = membership_criterion_category,
              domain_generator_method_id = script.id,
              parent_url=category.getRelativeUrl(),
              uid = category.getUid())

  domain_list.append(domain)

return domain_list
