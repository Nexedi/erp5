"""
  Use this function in local TioLive instance form to change global password for an user.
"""

portal = context.getPortalObject()
kw = {'reference': reference,
      'new_password': new_password,
      'old_password': old_password,
      'erp5_uid': portal.ERP5Site_getExpressInstanceUid()}
return portal.portal_wizard.callRemoteProxyMethod( \
                              distant_method = 'WitchTool_changeGlobalUserPasswordFromExpressInstance', \
                              use_cache = 0, \
                              ignore_exceptions = 0, \
                              **kw)
