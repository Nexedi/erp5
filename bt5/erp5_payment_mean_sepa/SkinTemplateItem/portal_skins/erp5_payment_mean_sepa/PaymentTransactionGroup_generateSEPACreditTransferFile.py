from Products.ERP5Type.Message import translateString

# Same check as in PaymentTransactionGroup_selectPaymentTransactionLineList
tag = 'PaymentTransactionGroup_selectPaymentTransactionList'
context.serialize()
if context.getPortalObject().portal_activities.countMessageWithTag(tag,):
  return context.Base_redirect(form_id, keep_items=dict(portal_status_message=translateString(
    "Some payments are still beeing processed in the background, please retry later")))

assert version == 'pain.001.001.02', 'Unsupported version'

portal = context.getPortalObject()

portal.portal_contributions.newContent(
    reference=context.getSourceReference(),
    data=getattr(context, 'PaymentTransactionGroup_viewAsSEPACreditTransferPain.001.001.02')().encode('utf-8'),
    filename=context.getSourceReference() + '.xml',
    # XXX we should probably use a dedicated type based method or preference,
    # for now we use the same as for *attached* documents.
    publication_section=context.getTypeBasedMethod('getPreferredAttachedDocumentPublicationSection')(),
    follow_up=context.getRelativeUrl(),
).release()

return context.Base_redirect(form_id, keep_items={
    'portal_status_message': translateString('SEPA Credit Transfer File generated.')
})
