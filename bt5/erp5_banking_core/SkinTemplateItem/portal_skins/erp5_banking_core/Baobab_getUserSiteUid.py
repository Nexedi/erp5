from Products.ERP5Type.Cache import CachingMethod

user_id = context.portal_membership.getAuthenticatedMember().getId()

def getUserSiteUid(user_id):
  return context.Baobab_getUserAssignedRootSite(user_id=user_id, object=1).getSiteUid()


getUserSiteUid = CachingMethod(getUserSiteUid, id='Baobab_getUserUserSiteUid', cache_factory='erp5_ui_medium')
return getUserSiteUid(user_id=user_id)
