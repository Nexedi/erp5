# try type of id
if id:
  try:
    long(id)
  except ValueError:
    raise KeyError("Item %s does not exists call by Python Script %s : not a long" % (id,
                                                                                               context.getTitle(),))

product_list = context.getProductList(*args, **kw)

product_dict = {}
variation_list = []

# First build list of product which are not variation
for product in product_list:
  if id:
    if product.getId() == id:
      product_dict[product.getId()] = product
    elif getattr(product, "parent_id", None) == id:
      variation_list.append(product)
  else:
    if not getattr(product, "parent_id", None):
      product_dict[product.getId()] = product
    else:
      variation_list.append(product)

variation_dict = {}
for variation in variation_list:
  parent_product_id = variation.parent_id
  product = product_dict[parent_product_id]
  if getattr(product, 'category', None) is None:
    setattr(product, 'category', [])
  # get options and their values
  product_category_combination = []
  for x in xrange(1, 4):
    base_category_id = getattr(variation, "base_category_id_%s" %(x), None)
    if base_category_id and int(base_category_id) != 0:
      context.log("trying to retrieve base category %s" %(base_category_id,))
      base_category = context.getBaseCategoryFromId(id=base_category_id)[0].id
      category_id = getattr(variation, "category_id_%s" %(x))
      category = context.getCategoryFromId(id=category_id)[0].id
      try:
        category = context.getParentValue().getCategoryFromMapping(
        category="%s/%s" %(base_category, category), create_mapping=True
        )
      except ValueError:
        context.log("impossible to get mapping for %s/%s" %(base_category, category))
        if id:
          return None
        else:
          return []
      if category not in product.category:
        product.category.append(category)
      product_category_combination.append(category)
  if len(product_category_combination):
    product_category_combination.sort()
    product.mapping_property_list.append({'reference' : getattr(variation, 'reference'),
                                          'category_list' : product_category_combination,})

if len(product_dict) == 0:
  return None
if id and len(product_dict):
 return product_dict.values()[0]
else:
  return product_dict.values()
