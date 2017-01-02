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
  # XXX to be finished
else:
  record = portal.restrictedTraverse(record_relative_url)

new_record = record.Base_createCloneDocument(batch_mode=True)
new_record.edit(
  title=context.getTitle(),
  date=context.getStartDate().Date().replace('/','-'),

  # Specific
  quantity=context.getPrice(),
  resource=context.getPriceCurrency(),
  resource_title=context.getPriceCurrencyTitle(),
  comment=context.getDescription(),
  latitude=context.getLatitude(),
  longitude=context.getLongitude(),
  )
new_record.setPhotoData(None)

new_record.stop()
new_record.Record_archivePreviousVersions()
