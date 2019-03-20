portal = context.getPortalObject()

line_list = []

for brain in portal.portal_simulation.getMovementHistoryList(
    portal_type=portal.getPortalAccountingMovementTypeList(),
    grouping_reference=grouping_reference,
    node_uid=node_uid,
    section_category=section_category,
    mirror_section_uid=mirror_section_uid):
  line = brain.getObject()
  line.setGroupingReference(None)
  line.setGroupingDate(None)
  line_list.append(line)

return line_list
