from Products.ERP5Type.Utils import cartesianProduct

line = []
column = []
tab = []

transformation = context.getParentValue()

# base_cell_id possible value: 'quantity', 'variation'
base_cell_id = 'quantity'
get_variation_base_category_method_dict = {
  'quantity': 'getQVariationBaseCategoryList',
  'variation': 'getVVariationBaseCategoryList'
}

# Those value are define on property sheet of portal type
line_base_category = transformation.getVariationBaseCategoryLine()
column_base_category = transformation.getVariationBaseCategoryColumn()

# Calculate line and column
for axe, axe_base_category in [(line, line_base_category), (column, column_base_category)]:
  clist = []
  #if axe_base_category in context.getVVariationBaseCategoryList():
  if axe_base_category in getattr(context, get_variation_base_category_method_dict[base_cell_id])():
    if matrixbox:
      # XXX matrixbox is right_display (not as listfield) => invert display and value in item
      axe.extend([(x[1], x[0]) for x in transformation.getVariationCategoryItemList(base_category_list = (axe_base_category,) )])
    else:
      axe.extend(transformation.getVariationCategoryList(base_category_list = (axe_base_category,) ))

# Calculate tab
# We can only display 3 dimension, so, we use a cartesian product to decrease matrix dimension
base_category_list = transformation.getVariationBaseCategoryList()
base_category = []

for c in base_category_list:
  if not c in (line_base_category, column_base_category):
    #if c in context.getVVariationBaseCategoryList():
    if c in getattr(context, get_variation_base_category_method_dict[base_cell_id])():
      if matrixbox:
        # XXX matrixbox is right_display (not as listfield) => invert display and value in item
        base_category.extend([(x[1], x[0]) for x in transformation.getVariationCategoryItemList(base_category_list = (c,)) ])
      else:
        base_category.extend(transformation.getVariationCategoryList(base_category_list = (c,)))

if len(base_category) > 0:
  # Then make a cartesian product
  # to calculate all possible combinations
  clist = cartesianProduct(base_category)

  # XXX is it possible to remove repr ?
  for c in clist:
    if matrixbox == 1:
      # XXX matrixbox is right display
      tab.append((repr([x[0] for x in c]), repr([x[1] for x in c])))
    else:
      tab.append( repr(c) )

# Try fill line first, then column, and after tab
for _ in range(2):
  if line == []:
    tmp = line
    line = column
    column = tmp
    tmp = None

  if column == []:
    tmp = column
    column = tab
    tab = tmp
    tmp = None

cell_range = [line, column, tab]
return cell_range
