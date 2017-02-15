record_brain_list = context.getPortalObject().portal_catalog(
  portal_type=portal_type,
  strict_follow_up_uid=context.getUid(),
  simulation_state="stopped",
  select_list=["creation_date", "relative_url"]
  )
if len(record_brain_list) > 1:
  current_record_brain = record_brain_list[0]
  for record_brain in record_brain_list:
    if current_record_brain.creation_date < record_brain.creation_date:
      current_record_brain.getObject().deliver()
      current_record_brain = record_brain
    # XXX Hackish
    elif current_record_brain.relative_url != record_brain.relative_url:
      record_brain.getObject().deliver()
  return current_record_brain.getObject()
elif len(record_brain_list) == 0:
  # No record found, not necessary to create one
  return None
return record_brain_list[0].getObject()
# XXX to be finished
