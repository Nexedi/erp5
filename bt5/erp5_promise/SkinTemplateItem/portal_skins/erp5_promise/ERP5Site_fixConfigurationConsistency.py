"""
"""
N_ = context.Base_translateString
if len(uids):
  for alarm in context.portal_alarms.searchFolder(uid=uids):
    alarm.solve()
    # Invoke activiveSense a bit later
    alarm.activate().activeSense()
  portal_status_message = N_("Site Configuration is going to be fixed by Activities.")
else:
  portal_status_message = N_("No Site Configuration fix was request.")

if enable_alarm:
  updated = False
  for alarm in context.portal_alarms.searchFolder(id="promise_%"):
    if not alarm.getEnabled():
      alarm.setEnabled(1)
      updated = True
  if updated:
    portal_status_message += N_("Consistency Check information will be periodically updated.")

form_id = context.REQUEST.get("form_id", "")

return context.Base_redirect(form_id,
                keep_items=dict(portal_status_message=portal_status_message))
