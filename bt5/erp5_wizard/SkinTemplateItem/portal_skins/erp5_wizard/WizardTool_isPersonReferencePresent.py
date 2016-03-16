reference = str(editor)
portal = context.getPortalObject()
return int(portal.portal_wizard.callRemoteProxyMethod(
                              'Base_isPersonReferencePresent', \
                              use_cache = 0, \
                              ignore_exceptions = 0, \
                              **{'reference':reference,
                                 'erp5_uid': context.ERP5Site_getExpressInstanceUid()}))
