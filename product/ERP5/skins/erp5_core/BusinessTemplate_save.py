## Script (Python) "BusinessTemplate_save"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id='', toxml=0
##title=Save a business template
##
REQUEST=context.REQUEST

f = context.portal_templates.save(context, toxml=toxml)

ret_url = context.absolute_url() + '/' + form_id
qs = '?portal_status_message=Saved+in+%s+.' % f

return REQUEST.RESPONSE.redirect( ret_url + qs )
