domain_list = []
if depth == 0:
  category_list = []
  for q in context.ProductionOrderModule_getSelectionProductionOrderList():
    specialise = q.getSpecialiseValue()
    if specialise is not None and specialise not in category_list:
      category_list.append(specialise)
else:
  return domain_list

for category in category_list:
  domain = parent.generateTempDomain(id = 'sub' + category.getId() )
  domain.edit(title = category.getTitle(),
              membership_criterion_base_category = ('specialise', ),
              membership_criterion_category = (category.getRelativeUrl(),),
              domain_generator_method_id = script.id,
              uid = category.getUid())

  domain_list.append(domain)

return domain_list
