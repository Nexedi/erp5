"""
  Get Person details (i.e. group, site, etc..) from its Career.
"""

from Products.ERP5Type.Cache import CachingMethod

def getPersonCareerDict(user_name):
  portal = context.getPortalObject()
  result = {'group_list': [],
            'site_list': [],
            }
  person = portal.Base_getUserValueByUserId(user_name)
  if person is None:
    return result

  group = person.getGroup()
  organisation = person.getSubordinationValue()
  if group is not None:
    result['group_list'] = [group]
  if organisation is not None:
    result['site_list'] = organisation.getSiteList()
  return result

getPersonCareerDict = CachingMethod(getPersonCareerDict,
                                    ("ERP5Site_getPersonCareerDict",),
                                    cache_factory='erp5_content_short')
return getPersonCareerDict(user_name)
