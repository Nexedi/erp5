## Script (Python) "BusinessTemplate_build"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id=''
##title=Build a business template
##
REQUEST=context.REQUEST

context.build()

ret_url = context.absolute_url() + '/' + form_id
qs = '?portal_status_message=Built.'

return REQUEST.RESPONSE.redirect( ret_url + qs )
