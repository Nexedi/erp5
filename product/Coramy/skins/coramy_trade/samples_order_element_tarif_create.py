## Script (Python) "samples_order_element_tarif_create"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id=''
##title=
##
request = context.REQUEST
order = context

order_line_list = order.contentValues(filter={'portal_type':'Sample Order Line'})
for order_line in order_line_list :
  elements_tarif_list = order_line.contentValues(filter={'portal_type':'Element Tarif'})

  order_line.invokeFactory(type_name="Element Tarif",
                      id="t"+str(len(elements_tarif_list)),
                      RESPONSE=request.RESPONSE)

redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , form_id
                              , 'portal_status_message=Eléments+de+tarif+créés.'
                              )

request[ 'RESPONSE' ].redirect( redirect_url )
