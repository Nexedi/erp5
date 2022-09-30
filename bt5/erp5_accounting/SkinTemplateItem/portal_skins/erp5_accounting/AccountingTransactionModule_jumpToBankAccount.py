# Jump to a bank account of the current organisation
Base_translateString = context.Base_translateString
request=context.REQUEST
portal = context.getPortalObject()
organisation = portal.restrictedTraverse(
          portal.portal_preferences.getPreferredAccountingTransactionSourceSection())

if organisation is not None :
  selection_uid_list = [ bank_account.getUid() for bank_account \
     in organisation.searchFolder(portal_type=portal.getPortalPaymentNodeTypeList()) ]
  if len(selection_uid_list) != 0 :
    kw = {'uid': selection_uid_list}
    portal.portal_selections.setSelectionParamsFor('Base_jumpToRelatedObjectList', kw)
    request.set('object_uid', context.getUid())
    request.set('uids', selection_uid_list)
    return context.Base_jumpToRelatedObjectList(
          uids=selection_uid_list, REQUEST=request)

return context.Base_redirect(form_id, keep_items=dict(portal_status_message=Base_translateString('No bank account for current organisation.')))
