## Script (Python) "BusinessTemplate_install"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id=''
##title=Build a business template
##
REQUEST=context.REQUEST

context.install()

ret_url = context.absolute_url() + '/' + form_id
qs = '?portal_status_message=Installed.'

return REQUEST.RESPONSE.redirect( ret_url + qs )
