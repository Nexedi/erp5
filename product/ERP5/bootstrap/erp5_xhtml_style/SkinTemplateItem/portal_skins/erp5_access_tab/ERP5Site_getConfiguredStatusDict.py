from Products.ERP5Type.Cache import CachingMethod

portal = context.getPortalObject()

def getConfiguredStatusDict():

  # Probe known skins to determine whether erp5_base and erp5_dms are installed.
  basic_mode = (getattr(context, 'Currency_view', None) is not None)
  dms_mode = (getattr(context, 'DocumentModule_viewDocumentList', None) is not None)

  express_pref_dict = context.ERP5Site_getExpressPreferenceDict()
  subscription_status = express_pref_dict.get('subscription_status')
  user_id = express_pref_dict.get('user_id')

  SUPPORT_ENABLED = 'support_enabled'
  SUPPORT_DISABLED = 'support_disabled'
  ADVERTISEMENT_ENABLED = 'advertisement_enabled'

  if getattr(portal, 'portal_wizard', None) is None:
    express_mode = SUPPORT_DISABLED
  elif subscription_status:
    if user_id:
      express_mode = SUPPORT_ENABLED
    else:
      express_mode = SUPPORT_DISABLED
  else:
    express_mode = ADVERTISEMENT_ENABLED
  return basic_mode, dms_mode, express_mode

getConfiguredStatusDict = CachingMethod(getConfiguredStatusDict, \
                                        id = 'ERP5Site_getConfiguredStatusDict', \
                                        cache_factory = 'erp5_ui_long')

basic_mode, dms_mode, express_mode = getConfiguredStatusDict()

# One more test for express
# If a user uses an account for configurator, only express tab will be displayed.
member = portal.portal_membership.getAuthenticatedMember()
role_list = list(member.getRoles())
role_list.sort()
getGroups = getattr(member, 'getGroups', None)
if role_list == ['Authenticated', 'Member'] and not getGroups():
  basic_mode = False
  dms_mode = False

return {'basic_mode': basic_mode,
        'dms_mode': dms_mode,
        'express_mode': express_mode,}
