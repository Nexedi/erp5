# get the current logged user site

from Products.ERP5Type.Cache import CachingMethod

if user_id is None:
  user_id = context.portal_membership.getAuthenticatedMember().getId()

def getFunctionList(user_id=user_id):

  valid_assignment = context.Baobab_getUserAssignment(user_id=user_id)

  function_list = []
  if valid_assignment != None:
    new_function_list = valid_assignment.getFunctionList()
    if len(new_function_list)>0:
      function_list.extend(new_function_list)
  return function_list

getFunctionList = CachingMethod(getFunctionList, id='Baobab_getUserAssignedFunctionList', 
                                cache_factory="erp5_ui_short")
return getFunctionList(user_id=user_id)
