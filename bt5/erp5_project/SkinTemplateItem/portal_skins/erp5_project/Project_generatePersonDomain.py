request = context.REQUEST
domain_list = []
object_path = request.get('object_path')
if object_path is None:
  object_path = context.REQUEST.get('URL1').split('/')[-1]

real_context = context.restrictedTraverse(object_path)

if depth == 0:
  category_list = context.portal_catalog(
    source_related_relative_url=(real_context.getRelativeUrl(), '%s/%%' % real_context.getRelativeUrl()),
  )
else:
  return domain_list

for category in category_list:
  domain = parent.generateTempDomain(id='sub%s' % category.getId())
  domain.edit(title=category.getTitle(),
              membership_criterion_base_category=('source',),
              membership_criterion_category=(category.getRelativeUrl(),),
              domain_generator_method_id=script.id,
              uid = category.getUid())
  domain_list.append(domain)

return domain_list
