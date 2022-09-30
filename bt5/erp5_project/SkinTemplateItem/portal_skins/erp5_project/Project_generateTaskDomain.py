request = context.REQUEST
domain_list = []
object_path = request.get('object_path')
if object_path is None:
  object_path = context.REQUEST.get('URL1').split('/')[-1]

search_path = 'project_module/%s/%%'

if depth == 0:
  category_list = []
  for line in context.portal_catalog(path=search_path ):
    category_list.extend([ i for i in line.getObject().getSourceProjectRelatedValueList() if i not in category_list])

else:
  return domain_list

for category in category_list:
  domain = parent.generateTempDomain(id = 'sub' + category.getId() )
  domain.edit(title = category.getTitle(),
              membership_criterion_base_category = ('source_project_related', ),
              membership_criterion_category = (category.getRelativeUrl(),),
              domain_generator_method_id = script.id,
              uid = category.getUid())

  domain_list.append(domain)

return domain_list
