reference = str(editor)
return int(context.portal_wizard.callRemoteProxyMethod(
                             'Base_isPersonReferenceUnique', \
                              use_cache = 0, \
                              ignore_exceptions = 0, \
                              **{'reference':reference,
                                 'ignore_users_from_same_instance':ignore_users_from_same_instance,
                                 'erp5_uid': context.ERP5Site_getExpressInstanceUid()}))
