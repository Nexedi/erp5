## Script (Python) "SalesPackingList_oneContainerAutoPackingSelectScript"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=method_action='', container_type='', delivery_mode='', gross_weight=''
##title=
##
# get the script
request = context.REQUEST

if method_action == 'SalesPackingList_oneContainerAutoPackingList':
  return context.SalesPackingList_oneContainerAutoPackingList(container_type=container_type, delivery_mode=delivery_mode, gross_weight=gross_weight)
elif method_action == 'SalesPackingList_oneContainerAutoPacking':
  return context.SalesPackingList_oneContainerAutoPacking(container_type=container_type, delivery_mode=delivery_mode, gross_weight=gross_weight)
else:
  redirect_url = '%s?%s' % ( context.absolute_url()
                            , 'portal_status_message=Erreur:+script+à+lancer+inconnu.'
                            )

  return request.RESPONSE.redirect( redirect_url )
