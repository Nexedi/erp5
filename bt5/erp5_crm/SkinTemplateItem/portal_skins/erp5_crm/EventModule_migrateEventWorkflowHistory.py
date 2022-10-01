portal = context.getPortalObject()
active_process = portal.portal_activities.newActiveProcess()
portal.event_module.recurseCallMethod(
  'Event_migrateEventWorkflowHistory',
  activate_kw=dict(active_process=active_process.getPath(),
                   group_method_cost=1),
  min_depth=1,
  max_depth=1)
print("Migration started with process id: %s" %active_process.getPath())
return printed
