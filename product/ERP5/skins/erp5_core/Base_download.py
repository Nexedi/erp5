## Script (Python) "Base_download"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
request=context.REQUEST
redirect_url = context.absolute_url()
return request.RESPONSE.redirect( redirect_url )
