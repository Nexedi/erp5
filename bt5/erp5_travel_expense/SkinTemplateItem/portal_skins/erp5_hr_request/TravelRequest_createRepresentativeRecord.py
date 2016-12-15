portal = context.getPortalObject()

if not record_relative_url:
  record_brain_list = portal.portal_catalog(
    portal_type="Travel Request Record",
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

new_record = record.Base_createCloneDocument(batch_mode=True)
new_record.edit(
  title=context.getTitle(),
  destination_reference=context.getReference(),
  start_date=context.getStartDate().Date().replace('/','-'),
  stop_date=context.getStopDate().Date().replace('/','-'),
  site=context.getAnimationCenter(),
  destination_node_title=context.getTravelDestination(),
  # XX Hackish
  comment=context.getDescription(),
  
  )
new_record.stop()
new_record.Record_archivePreviousVersions()
