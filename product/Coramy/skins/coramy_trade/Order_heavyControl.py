## Script (Python) "Order_heavyControl"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# This script makes controls on an order
# this script is called from a workflow_script during transitions
# return an error message ou empty string if ok

order = context
movement_list = []

# first make light control
error_message = order.Order_lightControl()

# then check every simulation_movement in relation with the order :
if order.getPortalType() == 'Purchase Order' :
  filter_dict = {'portal_type': 'Purchase Order Line'}
elif order.getPortalType() == 'Sales Order' :
  filter_dict = {'portal_type': 'Sales Order Line'}
else :
  filter_dict = {'portal_type': 'Production Order Line'}

movement_list += order.getOrderRelatedValueList(portal_type = 'Simulation Movement')
for order_line in order.contentValues(filter=filter_dict) :
  movement_list += order_line.getOrderRelatedValueList(portal_type = 'Simulation Movement')
  for cell in order_line.contentValues(filter={'portal_type': 'Delivery Cell'}) :
     movement_list += cell.getOrderRelatedValueList(portal_type = 'Simulation Movement')

# check each simulation movement :
for movement in movement_list :
  if movement.getTargetQuantity() != 0 and movement.getPrice() == 0  or \
     movement.getTargetQuantity() != 0 and movement.getPrice() == ''  or \
     movement.getTargetQuantity() != 0 and movement.getPrice() is None :
    if len(error_message) == 0 :
      error_message += 'Prix manquant: produit %s ou variante %s' % (movement.getResource(), movement.getVariationText())
    else :
      error_message += ' - Prix manquant: produit %s ou variante %s' % (movement.getResource(), movement.getVariationText())
    break

return error_message
