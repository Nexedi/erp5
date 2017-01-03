context.Base_prepareCorsResponse(RESPONSE=context.REQUEST.RESPONSE)
# XXX Base_download redirects to an HTML page on error !
#     So the client resend a request to the given HTML page (which is bad),
#     and CORS headers won't be set (which is correct) leading to
#     request failure on app.officejs !
return context.Base_download(*args, **kw)
