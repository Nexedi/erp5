## Script (Python) "sales_packing_list_secure_print"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id='', packing_list_page_template
##title=
##
packing_list = context
request = context.REQUEST

packing_list.flushActivity(invoke=1)

redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , packing_list_page_template
                              , 'portal_status_message=Impression+en+cours.'
                              )
request[ 'RESPONSE' ].redirect( redirect_url )
