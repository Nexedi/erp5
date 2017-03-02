"""
  Get Person assignment details.
"""

from Products.ERP5Type.Cache import CachingMethod

portal = context.getPortalObject()
result = {'group_list': [],
          'site_list': [],
          'function_list': [],
          'destination_trade_relative_url': None}
person = portal.Base_getUserValueByUserId(user_name)
if person is None:
  return result

def getAssignmentDict(username):
  person = portal.restrictedTraverse(person_relative_url)
  assignment_list = person.Person_getAvailableAssignmentValueList()
  for assignment in assignment_list:
    assignment = assignment.getObject()
    result['group_list'].extend([x for x in assignment.getGroupList() if x not in result['group_list']])
    result['function_list'].extend([x for x in assignment.getFunctionList() if x not in result['function_list']])
    result['site_list'].extend([x for x in assignment.getSiteList() if x not in result['site_list']])
    result['destination_trade_relative_url'] = assignment.getDestinationTradeRelativeUrl()
    result['destination_relative_url'] = assignment.getDestinationRelativeUrl()
  return result

person_relative_url = person.getRelativeUrl()
getAssignmentDict = CachingMethod(getAssignmentDict,
                               ("ERP5Site_getPersonAssignmentDict",),
                                cache_factory='erp5_ui_short')
return getAssignmentDict(person_relative_url)
