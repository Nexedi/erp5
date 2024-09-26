translateString = context.Base_translateString

if context.getSendState() != 'failed':
  return context.Base_redirect('Document_viewMailevaConnectionStatus',
    keep_items={'portal_status_message': translateString('This document is not in failed state')})

maileva_exchange = context.getFollowUpRelatedValue(portal_type='Maileva Exchange')
context.PDF_sendToMaileva(
  recipient = maileva_exchange.getDestinationValue(),
  sender = maileva_exchange.getSourceValue()
)
return context.Base_redirect('PDF_viewPDFJSPreview',
  keep_items={'portal_status_message': translateString('This document is resending to maileva')})
