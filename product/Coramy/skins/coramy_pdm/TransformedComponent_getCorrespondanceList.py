## Script (Python) "TransformedComponent_getCorrespondanceList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=transformation=None, quantities=1
##title=
##
transformed_component = context
correspondance_list = []

variation_base_category_list = []
q_variation_base_category_list = transformed_component.getQVariationBaseCategoryList()
v_variation_base_category_list = transformed_component.getVVariationBaseCategoryList()

if quantities :
  for base_category in q_variation_base_category_list :
    variation_base_category_list.append(base_category)

for base_category in v_variation_base_category_list :
  if not base_category in variation_base_category_list :
    variation_base_category_list.append(base_category)

variation_base_category_list.sort()
variation_list_list = []

for base_category in variation_base_category_list :
  variation_list = transformation.getVariationCategoryList(base_category_list = base_category)
  variation_list_list.append(variation_list)

cartesian_variation_list = context.cartesianProduct(variation_list_list)

mapped_value_list = context.objectValues()
for variation_list in cartesian_variation_list :
  quantity = ''
  variation = []
  for mapped_value in mapped_value_list :
    if mapped_value.test(transformed_component.asContext(categories=variation_list)) :
      if mapped_value.getId().find('quantity') <> (-1):
        try :
          quantity = str(mapped_value.getProperty(key='quantity'))
        except : pass
      if mapped_value.getId().find('variation') <> (-1):
        try :
          variation = mapped_value.getVariationCategoryList()
        except : pass

  if variation_list == [] and quantity == '' and  variation == [] :
    pass
  else :
    pretty_variation_1 = '- '
    for my_variation in variation_list :
      pretty_variation_1 += my_variation+' - '
    pretty_variation_2 = '- '
    for my_variation in variation :
      pretty_variation_2 += my_variation+' - '
    if pretty_variation_2 == '- ' :
      try :
        pretty_variation_2 += transformed_component.getVariationCategoryList()[0]
      except :
        pass
    if quantities :
      correspondance_list.append([pretty_variation_1, quantity, pretty_variation_2])
    else :
      correspondance_list.append([pretty_variation_1, '', pretty_variation_2])

return correspondance_list
