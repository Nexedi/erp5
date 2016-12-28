#if REQUEST is not None:
#  raise ValueError

portal = context.getPortalObject()
record = context
if record.getSimulationState() not in ("draft", "started"):
  return

# Is it the only new record
new_record_list = portal.portal_catalog(
  portal_type=record.getPortalType(),
  source_reference=record.getSourceReference(),
  strict_source_uid=record.getSourceUid(),
  simulation_state=('draft','started')
  )

if len(new_record_list) != 1:
  if record.getSimulationState() != "started":
    record.start(comment="Multiple similar records detected, please pick one")
    return
# It is the only record to be taken into account

if record.getSimulationState() != "started":
  record.start()
ticket_update_method = record.getTypeBasedMethod(
  "updateRelatedTicket",
  fallback_script_id="Record_updatedRelatedTicket"
  )

ticket_update_method()
