def asSecurityGroupId(self,**kw):
  ## Script (Python) "xERP5Type_asSecurityGroupId"
  ##bind container=container
  ##bind self=self
  ##bind namespace=
  ##bind script=script
  ##bind subpath=traverse_subpath
  ##parameters=category_order, **kw
  ##title=
  ##
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
  category_order=kw.get('category_order',None)
  if category_order not in (None, ''):
    category_order = list(category_order)
    category_order.sort()
  else:
    category_order = []

  for base_category in category_order:
   if kw.has_key(base_category):
    category_list   = kw[base_category]
    if type(category_list)==type(''):
      category_list = [category_list]
    for category in category_list:
      category_path   = '%s/%s' % (base_category, category)
      category_object = self.portal_categories.getCategoryValue(category_path)
      if category_object in (None, ''):
        raise "SecurityRoleDefinitionError", "Category '%s' doesn't exist" % (category_path)
      if category_object.getPortalType() == 'Person':
        # We define a person here
        user_name = category_object.getReference()
        if user_name is not None: user_list.append(user_name)
      elif category_object.getPortalType() == 'Project':
        # We use the project reference as a group
        category_code = category_object.getReference(category_object.getTitle())
        code_list.append(category_code)
      else:
        # We define a group item here
        category_code   = category_object.getCodification() or category_object.getId()
        code_list.append(category_code)

  # Return a list of users or a single group
  if user_list: 
    self.log('user_list',user_list)
    return user_list
  self.log('code_list',code_list)
  return '_'.join(code_list)
