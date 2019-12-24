"""
  Run Upgrade step

  IMPORTANT: Don't use the constraint_type upgrader to data migration or big amount of objects,
  because this step is suppose to run all constraints in the same transaction.
"""

portal = context.getPortalObject()

_, type_per_constraint_type = context.Base_getConstraintTypeListPerPortalType()
portal_type_list = type_per_constraint_type.get('upgrader', [])

tool_portal_type = 'Template Tool'
if tool_portal_type in portal_type_list:
  portal_type_list.remove(tool_portal_type)

activate_kw = params or {}

with context.defaultActivateParameterDict(activate_kw, placeless=True):
  active_process = context.newActiveProcess(activate_kw=activate_kw)

  method_kw = {'fixit': fixit,
    'filter_dict': {"constraint_type": 'upgrader'},
    'active_process': active_process.getRelativeUrl(),
    'activate_kw': activate_kw,
  }
  # always run on portal_templates, regardless of catalog state.
  portal.portal_templates.Base_postCheckConsistencyResult(**method_kw)
  # run on all portal_types with an `upgrader` constraint, except portal_templates we already run before.
  if portal_type_list:
    for result in portal.portal_catalog(portal_type=portal_type_list):
      result.Base_postCheckConsistencyResult(**method_kw)

context.setEnabled(False)
