## Script (Python) "Order_updateLocalRoles"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id=''
##title=
##
order = context
request = context.REQUEST

# what's the gestionaire of this order
user_name = ''
# are we on a sales order or puchase order ?
if order.getPortalType() == 'Sales Order' :
  user_name = order.getSourceAdministrationTitle().replace(' ','_')
elif order.getPortalType() in ('Purchase Order' , 'Production Order') :
  user_name = order.getDestinationAdministrationPersonTitle().replace(' ','_')

order.assign_gestionaire_designe_roles(user_name = user_name)

delivery_list = order.getCausalityRelatedValueList(portal_type=["Purchase Packing List", "Sales Packing List", "Production Packing List"])
for delivery in delivery_list :
  # update local_roles
  delivery.assign_gestionaire_designe_roles(user_name = user_name)

redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , form_id
                              , 'portal_status_message=Roles+mis+a+jour.'
                              )

request[ 'RESPONSE' ].redirect( redirect_url )
