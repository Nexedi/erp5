portal_type_list = context.EGov_getAllowedFormTypeList()
 
if portal_type_list == ():
  return []

# get portal_type_listuser name
user_name = context.portal_membership.getAuthenticatedMember().getIdOrUserName()

if not kw.has_key('portal_type'):
  kw['portal_type'] = portal_type_list
if not kw.has_key('sort_on'): 
  kw['sort_on']=[('modification_date', 'descending')]
result = context.portal_catalog(owner=user_name,
                                **kw)
return result
