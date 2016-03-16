'''
  This script return a Pay Sheet Line list with some new parameters on
  each Pay Sheet Line (like base, base_name, base_contribution_list,
  service,...)
  It's used in the PaySheetTransaction_view to display PaySheetLines
'''


from Products.ERP5Type.Utils import cartesianProduct
import pprint
from Products.ERP5Type.Message import translateString

portal = context.getPortalObject();
paysheet_line_list = context.contentValues(portal_type=('Pay Sheet Line', 'Pay Sheet Model Line'))
if context.getPriceCurrencyValue() is not None:
  precision = context.getPriceCurrencyValue().getQuantityPrecision()
else:
  precision = 2


line_list = []

for paysheet_line in paysheet_line_list:
  base_category_list = paysheet_line.getVariationBaseCategoryList()
  base_application_list = paysheet_line.getBaseApplicationTitleList()
  translated_base_application_list = [str(translateString(x)) for x in base_application_list]
  base_application_list = ', '.join(translated_base_application_list)
  service = paysheet_line.getResourceValue(portal_type='Service')
  base_contribution_list = paysheet_line.getBaseContributionList()
  causality = paysheet_line.getCausality()

  base_list = [str(translateString(base_application)) for base_application in \
      paysheet_line.getBaseApplicationTitleList()]
  base_name = '+'.join(base_list)

  list_of_list = []
  for base_category in base_category_list:
    list = paysheet_line.getVariationCategoryList(base_category_list=\
        base_category)
    list_of_list.append(list)
  cartesian_product = cartesianProduct(list_of_list)

  previous_share = None
  indice = 0

  if cartesian_product == [[]] or cartesian_product == []:
    params = {
                  'base':paysheet_line.getTotalPrice(),
                  'base_contribution_list':base_contribution_list,
                  'base_application_list': base_application_list,
                  'service': service is not None and\
                                      service.getId() or '',
                  'causality': causality,}
    line_list.append(paysheet_line.asContext(**params))
    continue

  object_dict = {}
  for product in cartesian_product:
    indice += 1
    share_dict = {}
    cell = paysheet_line.getCell(base_id='movement', *product)
    if cell is None:
      continue

    base = cell.getQuantity()

    cell_contribution_share = cell.getContributionShare() or ''
    share_dict[cell_contribution_share+'_price'] = cell.getPrice()
    share_dict[cell_contribution_share+'_quantity'] = cell.getQuantity()
    share_dict[cell_contribution_share+'_total_price'] = \
                    round(cell.getTotalPrice(), precision)

    tuple_dict = {}
    for item in product:
      # the dict key is the base category and value is the category path
      tuple_dict[item.split('/')[0]] = \
        portal.portal_categories.restrictedTraverse(item).getShortTitle() or \
        portal.portal_categories.restrictedTraverse(item).getTitle()
      tuple_dict[item.split('/')[0]+'_relative_url']=item

    # we want to display as lines as a paysheet line as slices
    # this is easier to read
    slice = cell.getSalaryRange()
    if slice is None:
      slice = 'no_slice'
    if not object_dict.has_key(slice):
      slice_title = None
      if tuple_dict.has_key('salary_range'):
        slice_title=tuple_dict['salary_range']
      object_dict[slice]={
                    'slice':slice_title,
                    'base_name':base_name,
                    'base':base,
                    'base_contribution_list':base_contribution_list,
                    'base_application_list': base_application_list,
                    'service': service is not None and\
                                        service.getId() or '',
                    'causality': causality,}
      object_dict[slice].update(share_dict)
    else:
      object_dict[slice].update(**share_dict)

  if not object_dict:
    # when the variation categories are set, but no cells.
    slice_title = None
    salary_range_list = [category for category in paysheet_line.getVariationCategoryList()
                                  if category.startswith('salary_range')]
    if salary_range_list:
      salary_range = portal.portal_categories.restrictedTraverse(salary_range_list[0])
      slice_title = salary_range.getShortTitle() or salary_range.getTitle()

    params = {
      'slice': slice_title,
      'base': paysheet_line.getTotalPrice(),
      'base_contribution_list': base_contribution_list,
      'base_application_list': base_application_list,
      'service': service is not None and\
                 service.getId() or '',
      'causality': causality,}
    line_list.append(paysheet_line.asContext(**params))
    continue

#  print pprint.pformat(object_dict)

  for object_key in paysheet_line.getSalaryRangeList():
    line_list.append(paysheet_line.asContext(**object_dict[object_key]))
  if object_dict.has_key('no_slice'):
    line_list.append(paysheet_line.asContext(**object_dict['no_slice']))



# sort results
def sortByTitleAscending(x, y):
  return cmp(x.getTitle(), y.getTitle())

def sortByTitleDescending(x, y):
  return cmp(y.getTitle(), x.getTitle())

def sortByIntIndexAscending(x, y):
  return cmp(x.getIntIndex(), y.getIntIndex())

def sortByIntIndexDescending(x, y):
  return cmp(y.getIntIndex(), x.getIntIndex())

sortByDefaultSortMethod = sortByIntIndexAscending

if kw.has_key('sort_on'):
  list = kw['sort_on']
  if list[0][0] == 'title' and list[0][1]=='ascending':
    line_list.sort(sortByTitleAscending)
  elif list[0][0] == 'title' and list[0][1]=='descending':
    line_list.sort(sortByTitleDescending)
  elif list[0][0] == 'int_index' and list[0][1]=='ascending':
    line_list.sort(sortByIntIndexAscending)
  elif list[0][0] == 'int_index' and list[0][1]=='descending':
    line_list.sort(sortByIntIndexDescending)
  else:
    line_list.sort(sortByDefaultSortMethod)
else:
  line_list.sort(sortByDefaultSortMethod)



return line_list
