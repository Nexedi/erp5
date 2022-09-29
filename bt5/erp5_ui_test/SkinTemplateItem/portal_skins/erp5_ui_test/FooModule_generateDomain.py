"""Special domains for foo"""
domain_list = []

if depth == 0:
  url = 'foo_category'
else:
  url = parent.getProperty('membership_criterion_category')

#context.log(script.id, 'parent = %r, context = %r, url = %r, depth = %r' % (parent, context, url, depth))

category_list = context.portal_categories.getCategoryValue(url).contentValues()
for category in category_list:
  domain = parent.generateTempDomain(id = category.getId())
  domain.edit(title = category.getTitle(),
              membership_criterion_base_category = ('foo_category',),
              membership_criterion_category = (category.getRelativeUrl(),),
              domain_generator_method_id = script.id,
              uid = category.getUid())

  domain_list.append(domain)

#context.log(script.id, 'parent = %r, category_list = %r, domain_list = %r' % (parent, category_list, domain_list))

return domain_list
