if not record_relative_url:
  record = context.Ticket_getLatestRepresentativeRecordValue(
    portal_type="Leave Request Record"
    )
else:
  record = context.getPortalObject().restrictedTraverse(record_relative_url)

if record is None:
  return "No records"

line_list = context.objectValues(portal_type="Leave Request Period")
if len(line_list) == 1:
  line = line_list[0]
else:
  raise ValueError("incorrect number of Leave Request Period in %s" % context.getRelativeUrl())

if context.getModificationDate() <= record.getCreationDate() \
    and line.getModificationDate() <= record.getCreationDate():
  # Nothing to do
  return "Nothing to do"


new_record = record.Base_createCloneDocument(batch_mode=True)
new_record.edit(
  title=context.getTitle(),
  destination_reference=context.getReference(),
  start_date=line.getStartDate(),
  stop_date=line.getStopDate(),
  comment=context.getDescription(),
  resource=line.getResource(),
  resource_tilte=line.getResourceTitle(),
  )
new_record.stop()
new_record.Record_archivePreviousVersions()

context.LeaveRequest_createPersonLeaveReport()
