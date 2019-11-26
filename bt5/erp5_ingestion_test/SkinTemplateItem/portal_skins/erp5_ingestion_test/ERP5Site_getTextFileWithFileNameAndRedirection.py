portal = context.getPortalObject()
context.REQUEST.RESPONSE.setHeader('content-type', 'text/plain')
context.REQUEST.RESPONSE.setHeader('Location', '%s/ERP5Site_getTextFileWithFileName?filename=%s&seed=%s' % (portal.absolute_url(), filename, seed))
context.REQUEST.RESPONSE.setStatus(302)
return ''
