from Products.ERP5Type.Message import translateString

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
