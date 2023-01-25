"""Central place to get document used to do the payment.
By default, use payment transaction. You can change this by override this script"""

return context.getPortalObject()\
      .SecurePaymentTool_createPaymentDocument(**kw)

# XXX DO WE NEED ANY COOKIE ?
# I (Seb) removed it, I don't understand why this is needed. Also
# because of this cookie, if there is any issue with the payment,
# it is totally impossible to do another payment without resetting cookies !
# most users don't even know that cookies exists, so this is really bad.

#request = context.REQUEST
#expire_timeout_days = 90
#session_id = request.get('session_id', None)
#portal_sessions = context.portal_sessions

#if session_id is None:
  ### first call so generate session_id and send back via cookie
  #now = DateTime()
  #session_id = context.Base_generateSessionID(max_long=20)
  #request.RESPONSE.setCookie('session_id', session_id, expires=(now +expire_timeout_days).fCommon(), path='/')

#if action=='reset':
  ### reset cart
  #portal_sessions.manage_delObjects(session_id)
#else:
  ### take payment transaction for this customer
  #session = portal_sessions[session_id]
  #payment_document_key = 'payment_document'
  #if not payment_document_key in session:
    #payment_document = context.getPortalObject()\
      #.SecurePaymentTool_createPaymentDocument(**kw)
    #session[payment_document_key] = payment_document.getRelativeUrl()

  ### return just a part of session for payment transaction
  #payment_document = context.restrictedTraverse(session[payment_document_key])
  #return payment_document
