"""Returns the list of section_uid for a group section_category.

This will only return organisations member of this section category.
If 'strict_membership' is true, then only organisations strictly member
of the category will be returned.
If no organisations are member of this section category, then [-1] is returned.
"""
portal = context.getPortalObject()

section = portal.portal_categories.restrictedTraverse(section_category)
return [x.uid for x in
            section.getGroupRelatedValueList(portal_type='Organisation',
                                             strict_membership=strict_membership,
                                             checked_permission='View')] or [-1]
