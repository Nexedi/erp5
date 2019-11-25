group_id_list_generator = getattr(context, 'ERP5Type_asSecurityGroupId')

security_category_dict = {}
# XXX This is a duplicate of logic present deep inside ERP5GroupManager.getGroupsForPrincipal()
# Please refactor into an accessible method so this code can be removed
def getDefaultSecurityCategoryMapping():
  return ((
    'ERP5Type_getSecurityCategoryFromAssignment',
    context.getPortalObject().getPortalAssignmentBaseCategoryList()
  ),)

getSecurityCategoryMapping = getattr(context, 'ERP5Type_getSecurityCategoryMapping', getDefaultSecurityCategoryMapping)
# XXX end of code duplication
for method_id, base_category_list in getSecurityCategoryMapping():
  try:
    security_category_dict.setdefault(tuple(base_category_list), []).extend(
      getattr(context, method_id)(base_category_list, login, context, ''))
  except Exception: # XXX: it is not possible to log message with traceback from python script
    print 'It was not possible to invoke method %s with base_category_list %s'%(method_id, base_category_list)

for base_category_list, category_value_list in security_category_dict.items():
  print 'base_category_list:', base_category_list
  for category_dict in category_value_list:
    print '-> category_dict:', category_dict
    print '-->', group_id_list_generator(category_order=base_category_list,
                                        **category_dict)
return printed
