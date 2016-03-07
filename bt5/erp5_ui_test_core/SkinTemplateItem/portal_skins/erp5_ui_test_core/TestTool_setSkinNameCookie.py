if skin_name:
  context.REQUEST.RESPONSE.setCookie('portal_skin', skin_name)
else:
  context.REQUEST.RESPONSE.expireCookie('portal_skin')
return context.REQUEST.RESPONSE.redirect(context.absolute_url())
