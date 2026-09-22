import json
portal_types = context.getPortalObject().portal_types
portal_type_tuple = tuple(context.Base_getContainedPortalTypeMappingDict(ignore_module_exclusion=True).keys())
return json.dumps({portal_type_id: portal_types.getDefaultModule(portal_type_id).getTitle() for portal_type_id in portal_type_tuple})
