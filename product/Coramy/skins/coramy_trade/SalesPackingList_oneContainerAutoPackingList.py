## Script (Python) "SalesPackingList_oneContainerAutoPackingList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=container_type='', delivery_mode='', gross_weight=''
##title=
##
# auto packing a list of container
request = context.REQUEST

object_list = context.object_action_list(selection_name='sales_packing_list_selection')
user_name = context.portal_membership.getAuthenticatedMember().getUserName()

for invoice in object_list:
  invoice.activate(activity="SQLQueue").SalesPackingList_oneContainerAutoPacking(container_type=container_type, delivery_mode=delivery_mode, gross_weight=gross_weight, user_name=user_name,batch_mode=1)

redirect_url = '%s?%s' % ( context.absolute_url(), 'portal_status_message=Autocolisage+démarré.')
return request[ 'RESPONSE' ].redirect( redirect_url )
