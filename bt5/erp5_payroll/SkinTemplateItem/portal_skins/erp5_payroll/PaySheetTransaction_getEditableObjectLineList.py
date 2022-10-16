"""
  This script return a list dictionary of editables services and
  all their usefull information that permit to display a popup
  to edit them.
  In base cases, only 'Monthly Labour' model line is editable (without any
  contribution_share or slice)
"""

from Products.ERP5Type.Utils import cartesianProduct
from Products.ERP5Type.Message import translateString

def sortByIntIndex(a, b):
  return cmp(a.getIntIndex(), b.getIntIndex())

portal_type_list = ['Pay Sheet Model Line']
sub_object_list = context.getInheritedObjectValueList(portal_type_list)
sub_object_list.sort(sortByIntIndex)
model_line_list = sub_object_list

# remove editable model line
model_line_list = [x.getObject() for x in model_line_list \
                            if x.getObject().isEditable()]

line_list = []
object_dict_list = []
id_ = 0

for model_line in model_line_list:
  base_category_list = model_line.getVariationBaseCategoryList()
  base_application_list = model_line.getBaseApplicationTitleList()
  translated_base_application_list = [str(translateString(x)) for x in base_application_list]
  base_application_list = ', '.join(translated_base_application_list)
  list_of_list = []
  for base_category in base_category_list:
    list_of_list.append(model_line.getVariationCategoryList(base_category_list=\
        base_category))
  cartesian_product = cartesianProduct(list_of_list)

  object_dict = {}

  if cartesian_product == [[]]:
    share_dict = {}
    continue

  for tuple_ in cartesian_product:
    share_dict = {}
    cell = model_line.getCell(*tuple_)
    if cell is None:
      continue

    quantity = cell.getQuantity()
    base = quantity

    base_list = [str(translateString(base_application)) for base_application in \
        model_line.getBaseApplicationTitleList()]
    base_name = '+'.join(base_list)

    service = model_line.getResourceValue()
    base_contribution_list = model_line.getBaseContributionList()

    price = cell.getPrice()
    if price is None:
      price = 1
    share_dict[cell.getContributionShare()+'_price'] = price
    share_dict[cell.getContributionShare()+'_quantity'] = quantity

    tuple_dict = {}
    for item in tuple_:
      # the dict key is the base category and value is the category path
      tuple_dict[item.split('/')[0]]=context.portal_categories.restrictedTraverse(item).getTitle()
      tuple_dict[item.split('/')[0]+'_relative_url']=item

    # we want to display as lines as a paysheet line as slices
    # this is easier to read

    salary_range = cell.getSalaryRange()
    # if there is no slice on a contribution, the dict key will be 'no_slice'
    # it could be just one 'no_slice' because a contribution have slice or not
    if salary_range is None:
      salary_range = 'no_slice'

    # check that another share on the same slice have not been already add
    if salary_range not in object_dict:
      salary_range_title = None
      salary_range_relative_url = None
      if 'salary_range' in tuple_dict:
        salary_range_title = tuple_dict['salary_range']
        salary_range_relative_url = tuple_dict['salary_range_relative_url']
      new_uid = "new_%s" % id_
      id_ += 1
      object_dict[salary_range]={
                    'uid':new_uid,
                    'salary_range_title':salary_range_title,
                    'salary_range_relative_url':salary_range_relative_url,
                    'base_name':base_name,
                    'base':base,
                    'model_line': model_line.getRelativeUrl(),
                    'base_contribution_list':base_contribution_list,
                    'base_application_list': base_application_list,
                    'service_id':service.getId()}
      object_dict[salary_range].update(share_dict)

    # if the slice already exists, just update the share
    else:
      object_dict[salary_range].update(share_dict)

  object_dict_list.append(object_dict)

  for object_key in model_line.getSalaryRangeList():
    line_list.append(model_line.asContext(**object_dict[object_key]))
  if 'no_slice' in object_dict:
    line_list.append(model_line.asContext(**object_dict['no_slice']))


if batch_mode:
  object_dict_list = [list(x.values())[0] for x in object_dict_list]
  return object_dict_list

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

if 'sort_on' in kw:
  sort_on = kw['sort_on']
  if sort_on[0][0] == 'title' and sort_on[0][1]=='ascending':
    line_list.sort(sortByTitleAscending)
  elif sort_on[0][0] == 'title' and sort_on[0][1]=='descending':
    line_list.sort(sortByTitleDescending)
  elif sort_on[0][0] == 'int_index' and sort_on[0][1]=='ascending':
    line_list.sort(sortByIntIndexAscending)
  elif sort_on[0][0] == 'int_index' and sort_on[0][1]=='descending':
    line_list.sort(sortByIntIndexDescending)
  else:
    line_list.sort(sortByDefaultSortMethod)
else:
  line_list.sort(sortByDefaultSortMethod)



#return pprint.pformat(line_list)
return line_list
