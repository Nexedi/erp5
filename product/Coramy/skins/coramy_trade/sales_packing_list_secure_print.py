## Script (Python) "sales_packing_list_secure_print"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id=''
##title=
##
packing_list = context
request = context.REQUEST

packing_list.flushActivity(invoke=1)

redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , 'sales_packing_list_print'
                              , 'portal_status_message=Mise+a+jour+en+cours.'
                              )
request[ 'RESPONSE' ].redirect( redirect_url )
