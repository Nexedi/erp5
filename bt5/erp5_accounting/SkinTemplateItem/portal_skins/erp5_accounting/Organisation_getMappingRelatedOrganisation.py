"""Returns the main organisation for that group.
"""

if len(context.contentValues(filter=
    dict(portal_type='Accounting Period'))) or context.getMapping():
  return context

def getOrganisationForSectionCategory(section):
  mapping = section.getMappingRelatedValue(portal_type='Organisation',
                           checked_permission='Access contents information')
  if mapping is not None:
    return mapping

  organisation_list = section.getGroupRelatedValueList(portal_type='Organisation',
                              strict_membership=1,
                              checked_permission='Access contents information')

  for organisation in organisation_list:
    if organisation.getProperty('validation_state', 'unset') not in ('deleted', 'invalidated'):
      return organisation


group = context.getGroupValue()
if group is None:
  return context

group_chain = []
while group.getPortalType() != 'Base Category':
  group_chain.append(group)
  group = group.getParentValue()

for group in group_chain:
  organisation = getOrganisationForSectionCategory(group)
  if organisation is not None and (
      len(organisation.contentValues(
              filter=dict(portal_type='Accounting Period'))) or
      organisation.getMapping()):
    return organisation

return context
