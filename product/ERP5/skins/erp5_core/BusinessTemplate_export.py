## Script (Python) "BusinessTemplate_export"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id='', toxml=0
##title=Export a business template
##
REQUEST=context.REQUEST
RESPONSE=REQUEST.RESPONSE

context.build()
s = context.portal_templates.manage_exportObject(id=context.getId(), toxml=toxml, download=1,
                                                 REQUEST=REQUEST, RESPONSE=RESPONSE)

return s
