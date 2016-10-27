portal_type_list = context.EGov_getAllowedFormTypeList()

validation_state_list=['archived',]

# get user name
user_name = context.portal_membership.getAuthenticatedMember().getIdOrUserName()

if not kw.has_key('portal_type'):
  kw['portal_type'] = portal_type_list
if not kw.has_key('sort_on'): 
  kw['sort_on']=[('modification_date', 'descending')]

kw['validation_state'] = validation_state_list

result = context.portal_catalog(owner=user_name,
                                **kw)
return result
