"""Resets grouping reference on this line and all related lines.

This runs by default asynchronously, but can be call with `async=False` to
run synchronously and returns the list of ungrouped lines. With `async=True`,
the returned list is always empty.
"""

if not context.getGroupingReference():
  # The line grouping reference can already have been removed, for example when two
  # lines of the same transaction have the same grouping reference.
  return []

portal = context.getPortalObject()

resetGroupingReference = portal.ERP5Site_resetAccountingTransactionLineGroupingReference
if async:
  resetGroupingReference = portal.portal_simulation.activate(
      activity='SQLQueue',
      after_tag='accounting_grouping_reference'
  ).ERP5Site_resetAccountingTransactionLineGroupingReference

ungrouped_line_set = set()
grouping_reference = context.getGroupingReference()
for (section_value, node_uid, mirror_section_uid) in (
  (context.getSourceSectionValue(), context.getSourceUid(), context.getDestinationSectionUid(),),
  (context.getDestinationSectionValue(), context.getDestinationUid(), context.getSourceSectionUid(),),
):
  if node_uid is not None and section_value is not None:
    section_value = section_value.Organisation_getMappingRelatedOrganisation()
    section_category = section_value.getGroup(base=True)
    if section_category:
      ungrouped_line_set.update(resetGroupingReference(
          section_category=section_category,
          node_uid=node_uid,
          mirror_section_uid=mirror_section_uid,
          grouping_reference=grouping_reference
      ) or [])
return list(ungrouped_line_set)
