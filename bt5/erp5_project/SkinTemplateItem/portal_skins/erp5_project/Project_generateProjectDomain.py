project_line_portal_type = 'Project Line'

domain_list = []

here = context.REQUEST['here']



if depth == 0:
  category_list = here.searchFolder(portal_type=project_line_portal_type, sort_on=(('int_index', 'ASC')))

else:
  category_list = []
  parent_category_list = parent.getMembershipCriterionCategoryList()
  for parent_category in parent_category_list:
    parent_category = '/'.join(parent_category.split('/')[1:])
    category_list.extend([x for x in context.restrictedTraverse(parent_category).searchFolder(portal_type=project_line_portal_type, sort_on=(('int_index', 'ASC')))])

i = 0
for category in category_list:
  domain = parent.generateTempDomain(id = '%s_%s' % (depth, i))
  domain.edit(title = category.getTitle(),
              membership_criterion_base_category = ('source_project', ),
              membership_criterion_category = ('source_project/' + category.getRelativeUrl(),),
              domain_generator_method_id = script.id,
              uid = category.getUid())
  i += 1

  domain_list.append(domain)

return domain_list
