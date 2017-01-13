portal = context.getPortalObject()

if not record_relative_url:
  record_brain_list = portal.portal_catalog(
    portal_type="Leave Request Record",
    strict_follow_up_uid=context.getUid(),
    simulation_state="stopped",
    )
  if len(record_brain_list) > 1:
    raise ValueError("Number of record superior to one")
  elif len(record_brain_list) == 0:
    return
  record= record_brain_list[0].getObject()
  # XXX to be finished
else:
  record = portal.restrictedTraverse(record_relative_url)

line_list = context.objectValues(portal_type="Leave Request Period")
if len(line_list) == 1:
  line = line_list[0]
else:
  raise ValueError("incorrect number of Leave Request Period in %s" % context.getRelativeUrl())


new_record = record.Base_createCloneDocument(batch_mode=True)
new_record.edit(
  title=context.getTitle(),
  destination_reference=context.getReference(),
  start_date=line.getStartDate(),
  stop_date=line.getStopDate(),
  comment=context.getDescription(),
  
  )
new_record.stop()
new_record.Record_archivePreviousVersions()
