alarm_tool = context.getPortalObject().portal_alarms
N_ = context.Base_translateString

for alarm in alarm_tool.searchFolder(id="promise_%"):
  alarm.activeSense()

portal_status_message = N_("Promises are been reloaded via activities, please wait for background activities finish.")
return context.Base_redirect("ERP5Site_viewCheckConsistency",
                    keep_items=dict(reset=1,
                                    portal_status_message=portal_status_message))
