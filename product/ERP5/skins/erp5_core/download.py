##parameters=

request=context.REQUEST
redirect_url = context.absolute_url()
return request.RESPONSE.redirect( redirect_url )
