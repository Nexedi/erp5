"""Returns the "main organisation" for that group, from accounting point of view.

Other organisation from this group are considered subsidiaries and have same
accounting periods as the main organisation. This is also used for invoice reconciliation.

XXX: the name of this script should include something "Accounting"
TODO: unify with Base_getAccountingPeriodStartDateForSectionCategory
"""
portal = context.getPortalObject()

def isMainOrganisation(organisation):
  return bool(organisation.contentValues(
    portal_type='Accounting Period',
    checked_permission='Access contents information'))

if isMainOrganisation(context):
  return context

group = context.getGroupValue()
if group is None:
  return context

while group.getPortalType() != 'Base Category':
  section_uid_list = portal.Base_getSectionUidListForSectionCategory(
      section_category=group.getRelativeUrl(),
      strict_membership=True)
  if -1 in section_uid_list:
    section_uid_list.remove(-1) # XXX explain this
  if section_uid_list:
    for brain in portal.portal_catalog(uid=section_uid_list):
      section = brain.getObject()
      if isMainOrganisation(section):
        return section
  group = group.getParentValue()
