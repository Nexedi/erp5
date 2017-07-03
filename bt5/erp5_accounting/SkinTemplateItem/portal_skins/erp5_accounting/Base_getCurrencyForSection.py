"""Returns the most suitable currency for a section.

If the section is an organisation, returns this organisation's accounting
currency.
If the section is a category, find the most suitable currency.

XXX consider using Base_getCurrencyForSectionCategory instead, because it supports
section_category_strict parameter and checks for duplicate currency used.
"""

def getCurrencyForSection(section_url):
  portal = context.getPortalObject()
  section = portal.portal_categories.restrictedTraverse(section_url)

  if section.getPortalType() == 'Organisation' and section.getPriceCurrency():
    return section.getPriceCurrency()

  if section.getPortalType() == 'Category':
    # first get the strict one
    member_list = section.getGroupRelatedValueList(portal_type='Organisation',
                                                   strict_membership=True,
                                                   checked_permission='View')
    for member in member_list:
      currency = member.getPriceCurrency()
      if currency:
        return currency

    # then from mapping category
    mapping = section.getMappingRelatedValue(portal_type='Organisation')
    if mapping is not None and mapping.getPriceCurrency():
      return mapping.getPriceCurrency()

    # otherwise, lookup all groups top down until we find one currency
    for subsection in section.getCategoryChildValueList(local_sort_id='int_index'):
      member_list = subsection.getGroupRelatedValueList(portal_type='Organisation',
                                        strict_membership=True,
                                        checked_permission='View')
      for member in member_list:
        currency = member.getPriceCurrency()
        if currency:
          return currency


from Products.ERP5Type.Cache import CachingMethod
getCurrencyForSection = CachingMethod(getCurrencyForSection,
                                      id=script.getId())
return getCurrencyForSection(section_url)
