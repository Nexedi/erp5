"""Resets grouping reference on this line and all related lines.

If the parameter keep_if_valid_group is true, then the grouping reference
will be kept as is if the group is still valid, ie. the total quantity
of all accounting lines in the group is 0.
Returns the list of ungroupped lines.
"""

if not context.getGroupingReference():
  # The line grouping reference can alredy have been removed, for example when two
  # lines of the same transaction have the same grouping reference.
  return []

portal = context.getPortalObject()
precision = context.getResourceValue(portal_type='Currency').getQuantityPrecision()

if context.AccountingTransaction_isSourceView():
  node_uid = context.getSourceUid()
  section_category = None
  section = context.getSourceSectionValue()
  if section is not None:
    section = section.Organisation_getMappingRelatedOrganisation()
    section_category = section.getGroup(base=1)
  mirror_section_uid = context.getDestinationSectionUid()
else:
  node_uid = context.getDestinationUid()
  section = context.getDestinationSectionValue()
  if section is not None:
    section = section.Organisation_getMappingRelatedOrganisation()
    section_category = section.getGroup(base=1)
  mirror_section_uid = context.getSourceSectionUid()

line_list = portal.portal_simulation.getMovementHistoryList(
                  portal_type=portal.getPortalAccountingMovementTypeList(),
                  grouping_reference=context.getGroupingReference(),
                  node_uid=node_uid,
                  section_category=section_category,
                  mirror_section_uid=mirror_section_uid)

# If the group is still valid, we may want to keep it as is.
if keep_if_valid_group and round(sum([(l.total_price or 0) for l in line_list]), precision) == 0:
  return

for line in line_list:
  line.setGroupingReference(None)
  line.setGroupingDate(None)

return line_list
