"""
  Run Upgrade step

  IMPORTANT: Don't use the constraint_type upgrader to data migration or big amount of objects,
  because this step is suppose to run all constraints in the same transaction. 
  To not kill the instance, searchAndActivate will be used if countResults() > REINDEX_SPLIT_COUNT
"""

REINDEX_SPLIT_COUNT = 100
portal = context.getPortalObject()
portal_alarms = portal.portal_alarms

_, type_per_constraint_type = context.Base_getConstraintTypeListPerPortalType()
portal_type_list = type_per_constraint_type.get('upgrader', [])

tool_portal_type = 'Template Tool' 
if tool_portal_type in portal_type_list:
  portal_type_list.remove(tool_portal_type)

activate_kw = params or {}

with context.defaultActivateParameterDict(activate_kw, placeless=True):
  active_process = context.newActiveProcess()

  method_kw = {'fixit': fixit,
    'filter': {"constraint_type": 'upgrader'},
    'active_process': active_process.getRelativeUrl(),
    'activate_kw': activate_kw,
  }

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
