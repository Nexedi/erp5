# get the current logged user site

from Products.ERP5Type.Cache import CachingMethod

if user_id is None:
  user_id = context.portal_membership.getAuthenticatedMember().getId()

def getSiteList(user_id=user_id):

  valid_assignment = context.Baobab_getUserAssignment(user_id=user_id)

  site_list = []
  if valid_assignment != None:
    new_site = valid_assignment.getSite()
    if not new_site.startswith('site'):
      new_site='site/%s' % new_site
    if new_site not in ('', None):
      site_list.append(new_site)
  return site_list

getSiteList = CachingMethod(getSiteList, id='Baobab_getUserAssignedSiteList', cache_factory='erp5_ui_short')
return getSiteList(user_id=user_id)
