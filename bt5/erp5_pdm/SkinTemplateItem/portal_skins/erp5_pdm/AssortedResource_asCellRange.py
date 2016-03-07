#  from Products.ERP5Type.Utils import cartesianProduct
# XXX unable to import cartesianProduct, so, I copied the code (Romain)
def cartesianProduct(list_of_list):
  if len(list_of_list) == 0:
    return [[]]
  result = []
  head = list_of_list[0]
  tail = list_of_list[1:]
  product = cartesianProduct(tail)
  for v in head:
    for p in product:
      result += [[v] + p]
  return result


line = []
column = []
tab = []

transformation = context.getParentValue()





#    security.declareProtected(Permissions.AccessContentsInformation, 'getQLineItemList')
#    def getQLineItemList(self, display_id='getTitle', base=1, current_category=None):
#      """
#      """
#      line_category = self._getSortedBaseCategoryList(self.getQVariationBaseCategoryList())[0]
#      #LOG('getQLineItemList', 0, "%s" % str(line_category))
#      if line_category is None:
#        result = [(None,'')]
#      else:
#        result = self.getVariationRangeCategoryItemList(base_category_list = [line_category],
#                                                        display_id=display_id,
#                                                        base=base,
#                                                        current_category=current_category)
#      #LOG('getQLineItemList', 10, "%s" % str(result))
#      return result

#    security.declareProtected(Permissions.AccessContentsInformation, 'getQColumnItemList')
#    def getQColumnItemList(self, display_id='getTitle', base=1, current_category=None):
#      """
#      """
#      column_category = self._getSortedBaseCategoryList(self.getQVariationBaseCategoryList())[1]
#      #LOG('getQColumnItemList', 0, "%s" % str(column_category))
#      if column_category is None:
#        result = [(None,'')]
#      else:
#        result = self.getVariationRangeCategoryItemList(base_category_list = [column_category],
#                                                        display_id=display_id,
#                                                        base=base,
#                                                        current_category=current_category)
#      #LOG('getQColumnItemList', 0, "%s" % str(result))
#      return result

#    security.declareProtected(Permissions.AccessContentsInformation, 'getQTabItemList')
#    def getQTabItemList(self, display_id='getTitle', base=1, current_category=None):
#      """
#        Returns a list of items which can be used as index for
#        each tab of a matrix or to define a cell range.
#      """
#      tab_category_list = self._getSortedBaseCategoryList(self.getQVariationBaseCategoryList())[2:]
#      tab_category_item_list_list = []
#      for tab_category in tab_category_list:
#        tab_category_item_list = self.getVariationRangeCategoryItemList(base_category_list = [tab_category],
#                                                                        display_id=display_id,
#                                                                        base=base,
#                                                                        current_category=current_category)
#        tab_category_item_list_list.append(tab_category_item_list)
#      transformation = self.getParentValue()
#      transformation_category_item_list = transformation.getVariationCategoryItemList(
#                                                          display_id=display_id,
#                                                          base=base,
#                                                          current_category=current_category)
#      tab_category_item_list_list.append(transformation_category_item_list)
#      if len(tab_category_item_list_list) > 0:
#        product_list = cartesianProduct(tab_category_item_list_list)
#        result = []
#        for item_list in product_list:
#          value_list = []
#          label_list = []
#          for item in item_list:
#            value_list.append(item[0])
#            label_list.append(item[1])
#          result.append((value_list, label_list))
#      else:
#        result = [(None,'')]
#      return result

































































# base_cell_id possible value: 'quantity', 'variation'
base_cell_id = 'quantity'
get_variation_base_category_method_dict = {
  'quantity': 'getQVariationBaseCategoryList',
  'variation': 'getVVariationBaseCategoryList'
}


#  from Products.ERP5Type.Utils import cartesianProduct
# XXX unable to import cartesianProduct, so, I copied the code (Romain)
def cartesianProduct(list_of_list):
  if len(list_of_list) == 0:
    return [[]]
  result = []
  head = list_of_list[0]
  tail = list_of_list[1:]
  product = cartesianProduct(tail)
  for v in head:
    for p in product:
      result += [[v] + p]
  return result


line = []
column = []
tab = []

transformation = context.getParentValue()

# Those value are define on property sheet of portal type
line_base_category = transformation.getVariationBaseCategoryLine()
column_base_category = transformation.getVariationBaseCategoryColumn()

# Calculate line and column
for axe, axe_base_category in [(line, line_base_category),(column, column_base_category)]:
  clist = []
  #if axe_base_category in context.getVVariationBaseCategoryList():
  if axe_base_category in getattr(context, get_variation_base_category_method_dict[base_cell_id])():

    if matrixbox == 1:
      # XXX matrixbox is right_display (not as listfield) => invert display and value in item
      axe += map(lambda x: (x[1],x[0]), transformation.getVariationCategoryItemList(base_category_list = (axe_base_category,) ) )
    else:
      axe += transformation.getVariationCategoryList(base_category_list = (axe_base_category,) )

# Calculate tab
# We can only display 3 dimension, so, we use a cartesian product to decrease matrix dimension
base_category_list = transformation.getVariationBaseCategoryList()
base_category = []

for c in base_category_list:
  if not c in (line_base_category, column_base_category):
    #if c in context.getVVariationBaseCategoryList():
    if c in getattr(context, get_variation_base_category_method_dict[base_cell_id])():
      if matrixbox == 1:
        # XXX matrixbox is right_display (not as listfield) => invert display and value in item
        base_category += [ map(lambda x: (x[1],x[0]), transformation.getVariationCategoryItemList(base_category_list = (c,) )) ]
      else:
        base_category += [ transformation.getVariationCategoryList(base_category_list = (c,) ) ]

if len(base_category) > 0:
  # Then make a cartesian product
  # to calculate all possible combinations
  clist = cartesianProduct(base_category)
  
  # XXX is it possible to remove repr ?
  for c in clist:
    if matrixbox == 1:
      # XXX matrixbox is right display
      tab.append(  ( repr(map(lambda x: x[0], c)) , repr(map(lambda x: x[1], c)) ) )
    else:
      tab.append( repr(c) )

# Try fill line first, then column, and after tab
for i in range(2):
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
