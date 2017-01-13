# get user name
user_name = context.portal_membership.getAuthenticatedMember().getIdOrUserName()

if not kw.has_key('portal_type'):
  kw['portal_type'] = context.getPortalDocumentTypeList()
if not kw.has_key('sort_on'): 
  kw['sort_on']=[('modification_date', 'descending')]
return context.portal_catalog(owner=user_name,
                              **kw);
