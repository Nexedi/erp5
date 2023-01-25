if not record_relative_url:
  record = context.Ticket_getLatestRepresentativeRecordValue(
    portal_type="Travel Request Record"
    )
else:
  record = context.getPortalObject().restrictedTraverse(record_relative_url)

if record is None:
  return

if context.getModificationDate() <= record.getCreationDate():
  # Nothing to do
  return

new_record = record.Base_createCloneDocument(batch_mode=True)
new_record.edit(
  title=context.getTitle(),
  destination_reference=context.getReference(),
  start_date=context.getStartDate(),
  stop_date=context.getStopDate(),
  site=context.getAnimationCenter(),
  destination_node_title=context.getTravelDestination(),
  # XX Hackish
  resource=context.getResource(),
  resource_title=context.getResourceTitle(),
  comment=context.getDescription(),

  )
new_record.stop()
new_record.setTransitionComment(context.Ticket_generateTransitionAndCommentList(listbox_view=False))
new_record.Record_archivePreviousVersions()
