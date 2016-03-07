source = context.getSourceSectionValue()
section_category = context.portal_preferences\
         .getPreferredAccountingTransactionSectionCategory()
section_category_strict = context.portal_preferences\
         .getPreferredAccountingSectionCategoryStrict()

# If the source is an organisation member of the preferred section category,
# then we'll show the source view
if source is not None and section_category:
  if source.getPortalType() == 'Person':
    return False
  if source.isMemberOf(section_category,
                       strict_membership=section_category_strict):
    return True

# Else, if the destination is an organisation member of the preferred section category,
# then we'll not show source view
destination = context.getDestinationSectionValue()
if destination is not None and section_category:
  if destination.getPortalType() == 'Person':
    return True
  if destination.isMemberOf(section_category,
                            strict_membership=section_category_strict):
    return False

# If we reach this point, none of the sections are member of the preferred section
# category, we'll then show source view, default for this script
return True
