constraint_type_per_type, _ = context.Base_getConstraintTypeListPerPortalType()
constraint_type = filter_dict.get("constraint_type")
if not constraint_type:
  return

if activate_kw is None:
  activate_kw = {}

if filter_dict is None:
  filter_dict = {}


portal_type_list = []
append = portal_type_list.append
for portal_type, constraint_type_list in constraint_type_per_type.iteritems():
  if constraint_type in constraint_type_list:
    append(portal_type)

if portal_type_list:
  context.getPortalObject().portal_catalog.searchAndActivate(
    'Base_postCheckConsistencyResult',
    activate_kw=activate_kw,
    portal_type=portal_type_list,
    method_kw={
      'fixit': fixit,
      'filter_dict': filter_dict,
      'active_process': active_process.getRelativeUrl(),
      'activate_kw': activate_kw,
    },
  )
