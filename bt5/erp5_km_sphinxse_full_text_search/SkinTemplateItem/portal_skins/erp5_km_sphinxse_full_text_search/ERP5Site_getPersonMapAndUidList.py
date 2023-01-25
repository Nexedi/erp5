"""
  Examine ERP5 Site return mapping between a 'reference' and respective Person object's title.
  This script is used in "No ZODB" approach to get fast search results.
"""
from Products.ERP5Type.Cache import CachingMethod

def getPersonMapAndUidList():
  result_dict = {}
  kw['portal_type'] = 'Person'
  kw['reference'] = '!=Null'
  person_list = context.portal_catalog(**kw)
  for person in person_list:
    person = person.getObject()
    result_dict[person.getReference()] = {'title': person.getTitle(),
                                        'path': person.getPath()}
  return result_dict

getPersonMapAndUidList = CachingMethod(getPersonMapAndUidList,
                                      id = 'ERP5Site_getPersonMapAndUidList',
                                      cache_factory = 'erp5_content_medium')
return getPersonMapAndUidList()
