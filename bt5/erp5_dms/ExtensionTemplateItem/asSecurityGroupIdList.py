from Products.ERP5Type.Utils import cartesianProduct

def asSecurityGroupIdList(self, category_order=None, **kw):
  # category_order : list of base_categories we want to use to generate the group id
  # kw : keys should be base categories,
  #      values should be value of corresponding relative urls (obtained by getBaseCategory())
  #
  # Example call : self.ERP5TypeSecurity_asGroupId(category_order=('site', 'group', 'function'),
  #                    site='france/lille', group='nexedi', function='accounting/accountant')
  # This will generate a string like 'LIL_NXD_ACT' where "LIL", "NXD" and "ACT" are the codification
  #   of respecively "france/lille", "nexedi" and "accounting/accountant" categories
  #
  # ERP5Type_asSecurityGroupId can also return a list of users whenever a category points
  # to a Person instance. This is useful to implement user based local role assignments
  code_list = []
  user_list = []

  # sort the category list lexicographically
  # this prevents us to choose the exact order we want,
  # but also prevents some human mistake to break everything by creating site_function instead of function_site
  if category_order not in (None, ''):
    category_order = list(category_order)
    category_order.sort()
  else:
    category_order = []

  code_dict = {}
  for base_category in category_order:
    code_dict[base_category] = []
    category_list   = kw[base_category]
    if isinstance(category_list, str):
      category_list = [category_list]
    for category in category_list:
      category_path   = '%s/%s' % (base_category, category)
      category_object = self.portal_categories.getCategoryValue(category_path)
      if category_object in (None, ''):
        raise RuntimeError, "Category '%s' doesn't exist" % (category_path)
      if category_object.getPortalType() == 'Person':
        # We define a person here
        user_name = category_object.getReference()
        if user_name is not None: user_list.append(user_name)
      else:
        # We define a group item here
        try:
          category_code   = category_object.getCodification()
        except AttributeError:
          category_code = category_object.getReference()
        if category_code not in code_dict[base_category]:
          code_dict[base_category].append(category_code)
        if base_category=='site':
          category_object = category_object.getParentValue()
          while category_object.getPortalType()!='Base Category':
            # LOG('checking category_object:',0,category_object.getRelativeUrl())
            category_code = category_object.getCodification()
            if category_code is not None and category_code not in code_dict[base_category]:
              code_dict[base_category].append(category_code)
            category_object = category_object.getParentValue()
        #code_list.append(category_code)

  # Return a list of users or a single group
  #LOG('asSecurityGroupIdList, user_list',0,user_list)
  if user_list: return user_list

  # LOG('asSecurityGroupIdList, code_dict',0,code_dict)
  def getCombinationList(item_list):
    if len(item_list):
      result = getCombinationList(item_list[1:])
      return [item_list[:1] + x for x in result] + result
    return [[]]

  code_list_of_list = []
  for base_category in category_order:
    code_list_of_list.append(code_dict[base_category])
  full_code_list = []
  for code_list in cartesianProduct(code_list_of_list):
    for x in getCombinationList(code_list):
      if len(x):
        # we have to sort it to match these in object local roles
        x.sort()
        full_code_list.extend(['_'.join(x) ])

  #LOG('asSecurityGroupIdList, result',0,['_'.join(x) for x in getCombinationList(code_list) if len(x)])
  #return ['_'.join(x) for x in getCombinationList(code_list) if len(x)]
  #LOG('asSecurityGroupIdList', 0,  'return full_code_list = %s' %(full_code_list,))
  self.log('full_code_list',full_code_list)
  return full_code_list
