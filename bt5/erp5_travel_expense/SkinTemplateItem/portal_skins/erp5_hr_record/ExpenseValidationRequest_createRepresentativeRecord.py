if not record_relative_url:
  record = context.Ticket_getLatestRepresentativeRecordValue(
    portal_type="Expense Record"
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
  date=context.getStartDate().Date().replace('/','-'),

  # Specific
  quantity=context.getPrice(),
  resource=context.getPriceCurrency(),
  resource_title=context.getPriceCurrencyTitle(),
  comment=context.getDescription(),
  latitude=context.getLatitude(),
  longitude=context.getLongitude(),
  type=context.getResource(),
  type_title=context.getResourceTitle(),
  )
new_record.setPhotoData(None)
new_record.setTransitionComment(context.Ticket_generateTransitionAndCommentList(listbox_view=False))
new_record.stop()
new_record.Record_archivePreviousVersions()
