"""Returns the main organisation for a section_category.

"""
portal = context.getPortalObject()

def getOrganisationForSectionCategory(section_category):
  section = portal.portal_categories.restrictedTraverse(section_category)

  mapping = section.getMappingRelatedValue(portal_type='Organisation',
                           checked_permission='Access contents information')
  if mapping is not None:
    return mapping.getRelativeUrl()

  organisation_list = section.getGroupRelatedValueList(portal_type='Organisation',
                              strict_membership=1,
                              checked_permission='Access contents information') + \
                      section.getGroupRelatedValueList(portal_type='Organisation',
                              checked_permission='Access contents information')

  for organisation in organisation_list:
    if organisation.getProperty('validation_state', 'unset') not in ('deleted', 'cancelled'):
      return organisation.getRelativeUrl()


from Products.ERP5Type.Cache import CachingMethod
getOrganisationForSectionCategory = CachingMethod(getOrganisationForSectionCategory,
                                                  id=script.getId())
organisation_url = getOrganisationForSectionCategory(section_category)
if organisation_url:
  return portal.restrictedTraverse(organisation_url, None)
