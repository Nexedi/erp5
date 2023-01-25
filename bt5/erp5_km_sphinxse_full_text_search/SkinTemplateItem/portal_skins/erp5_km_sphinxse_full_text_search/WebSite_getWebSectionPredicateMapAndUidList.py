"""
  Examine Web Site's Web Sections and return mapping between sections' uid and respective
  category used in sections' predicate.
  This script is used in "No ZODB" approach to get fast search results (including list of
  sections a object belongs to).
"""
from Products.ERP5Type.Cache import CachingMethod

website = context.getWebSiteValue()

def getWebSectionList(section):
  result = [{'uid': section.getUid(),
             'relative_url': section.getRelativeUrl(),
             'membership_base_category_list': section.getMembershipCriterionBaseCategoryList(),
             'multi_membership_base_category_list': section.getMultimembershipCriterionBaseCategoryList(),
             'membership_category_list': section.getMembershipCriterionCategoryList()}]
  for section in section.contentValues(portal_type='Web Section'):
    result.extend(getWebSectionList(section))
  return result

def getWebSectionPredicateValueList():
  category_map = {}
  base_category_uid_list = []
  portal_categories = context.portal_categories
  for section in getWebSectionList(website):
    # calc category_path : section map
    for category in section['membership_category_list']:
      # remove leading 'follow_up' from category
      if category.startswith('follow_up/'):
        category = category.replace('follow_up/', '', 1)
      if category not in category_map:
        category_map[category] = []
      category_map[category].append({'uid': section['uid'], 'relative_url':section['relative_url']})
    # get base_categories we care for
    section_category_list = section['membership_base_category_list']+section['multi_membership_base_category_list']
    for category_id in section_category_list:
      category = getattr(portal_categories, category_id, None)
      if category is not None and category.getUid() not in base_category_uid_list:
        base_category_uid_list.append(category.getUid())
  return category_map, base_category_uid_list

getWebSectionPredicateValueList = CachingMethod(getWebSectionPredicateValueList,
                                      id = 'WebSite_getWebSectionPredicateMapAndUidList',
                                      cache_factory = 'erp5_content_medium')
return getWebSectionPredicateValueList()
