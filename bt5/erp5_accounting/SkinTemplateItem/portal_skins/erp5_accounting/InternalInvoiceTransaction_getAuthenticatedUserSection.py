'''Returns the relative url of the section for the current user.

If the user is only affected to one of the two involved sections' group, then we return this section. This is the most common case.
If the user is affected to both sections, then we use the user preference.
'''

person = context.getPortalObject().portal_membership.getAuthenticatedMember().getUserValue()
if person is None:
  return ''

from DateTime import DateTime
now = DateTime()

assigned_group_set = set() # groups on which the user is assigned
for assignment in person.contentValues(portal_type='Assignment'):
  if assignment.getGroup() \
      and assignment.getValidationState() == 'open' \
      and ( assignment.getStartDate() is None or
            assignment.getStartDate() <= now <= assignment.getStopDate()):
    assigned_group_set.add(assignment.getGroup())


valid_group_set = set() # groups on which the user is assigned and are used in this invoice
for section in (context.getSourceSectionValue(),
                context.getDestinationSectionValue()):
  if section is not None:
    group = section.getGroup()
    if group and group in assigned_group_set:
      valid_group_set.add(section.getRelativeUrl())

if len(valid_group_set) == 1:
  return valid_group_set.pop()
elif len(valid_group_set) == 2:
  # the user is assigned to both groups, then we look if his preference matches one of the group of the section.
  preferred_section = context.getPortalObject().portal_preferences.getPreferredAccountingTransactionSourceSection()
  if preferred_section in valid_group_set:
    return preferred_section
  raise ValueError("You are assigned on both source and destination section of this invoice but your preferred section does not match any.")

return ''
