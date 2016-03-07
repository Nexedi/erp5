"""
  Run Upgrader

  IMPORTANT: Don't use the constraint_type upgrader to data migration or big amount of objects,
  because this step is suppose to run all constraints in the same transaction. 
  To not kill the instance, searchAndActivate will be used if countResults() > REINDEX_SPLIT_COUNT
"""

REINDEX_SPLIT_COUNT = 100
portal = context.getPortalObject()
portal_alarms = portal.portal_alarms
active_process = context.newActiveProcess()

# We should not run upgrader if pre upgrade was not solved or never executed 
alarm = getattr(portal_alarms, 'upgrader_check_pre_upgrade')
if not(force) and alarm.sense() in (None, True):
  active_process.postActiveResult(summary=context.getTitle(),
      severity=1,
      detail=["Is required solve Pre Upgrade first. You need run active sense once at least on this alarm"])
  return

_, type_per_constraint_type = context.Base_getConstraintTypeListPerPortalType()
portal_type_list = type_per_constraint_type.get('upgrader', [])

tool_portal_type = 'Template Tool' 
if tool_portal_type in portal_type_list:
  portal_type_list.remove(tool_portal_type)

method_kw = {'fixit': True,
  'filter': {"constraint_type": 'upgrader'},
  'active_process': active_process.getRelativeUrl()}

portal.portal_templates.Base_postCheckConsistencyResult(**method_kw)
for portal_type in portal_type_list:
  if portal.portal_catalog.countResults(
      portal_type=portal_type_list)[0][0] > REINDEX_SPLIT_COUNT:
    portal.portal_catalog.searchAndActivate('Base_postCheckConsistencyResult',
      activate_kw=activate_kw,
      portal_type=portal_type,
      method_kw=method_kw)
  else:
    for result in portal.portal_catalog(portal_type=portal_type):
      result.Base_postCheckConsistencyResult(**method_kw)

context.setEnabled(False)
return
