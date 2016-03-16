portal = context.getPortalObject()
portal.portal_sessions.manage_delObjects(portal.Base_getAutoLogoutSessionKey())
# XXX: I would like to use skinSuper, but this may not be defined on context (it's defined on ERP5Type.Base, and context may be ERP5.ERP5Site).
# As a result, hardcode expected logout location (which is marginally better than duplicating it).
return portal.portal_skins.zpt_control.logout()
