request = context.REQUEST

project_line_portal_type = 'Project Line'
domain_list = []

object_path = request.get('object_path')
if object_path is None:
  # Sometimes the object_path not comes with the request, when you edit for example.
  object_path = context.REQUEST.get('URL1').split('/')[-1]

domain_list = []

if depth == 0:
  category_list = [context.project_module.restrictedTraverse(object_path)]
else:
  category_list = []
  parent_category_list = parent.getMembershipCriterionCategoryList()
  for parent_category in parent_category_list:
    parent_category = '/'.join(parent_category.split('/')[1:])
    category_list.extend(context.restrictedTraverse(parent_category).contentValues(portal_type=project_line_portal_type))

i=0
for category in category_list:
  domain = parent.generateTempDomain(id = '%s_%s' % (depth, i))
  domain.edit(title = category.getTitle(),
              membership_criterion_base_category = ('source_project', ),
              membership_criterion_category = (category.getRelativeUrl(), ),
              domain_generator_method_id = script.id,
              uid = category.getUid())
  i += 1
  domain_list.append(domain)

return domain_list
