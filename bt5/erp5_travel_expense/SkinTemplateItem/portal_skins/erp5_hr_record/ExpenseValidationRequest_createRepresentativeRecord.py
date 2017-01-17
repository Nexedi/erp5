portal = context.getPortalObject()

if not record_relative_url:
  record_brain_list = portal.portal_catalog(
    portal_type="Expense Record",
    strict_follow_up_uid=context.getUid(),
    simulation_state="stopped",
    )
  if len(record_brain_list) > 1:
    raise ValueError("Number of record superior to one")
  elif len(record_brain_list) == 0:
    return
  record= record_brain_list[0].getObject()
  #XXX Record_archivePreviousVersions deliver this record, but may not index yet
  if record.getSimulationState() != 'stopped':
    return
  # XXX to be finished
else:
  record = portal.restrictedTraverse(record_relative_url)





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
