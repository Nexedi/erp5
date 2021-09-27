if context.getSendState() != 'failed':
  return context.Base_redirect('Document_viewMailevaConnectionStatus', keep_items={'portal_status_message': 'This document is not in failed state'})

maileva_exchange = context.getFollowUpRelatedValue(portal_type='Maileva Exchange')
context.activate().PDF_sendToMailevaByActivity(
  recipient = maileva_exchange.getDestination(),
  sender = maileva_exchange.getSource(),
  connector = maileva_exchange.getResource()
)
context.send()
return context.Base_redirect('PDF_viewPDFJSPreview', keep_items={'portal_status_message': 'This document is resending to maileva'})
