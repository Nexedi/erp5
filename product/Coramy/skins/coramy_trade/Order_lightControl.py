## Script (Python) "Order_lightControl"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# This script makes a few controls on an order
# this script is called from a workflow_script during transitions
# return an error message ou empty string if ok

error_message = ''
order = context

# check if profile is completete
if order.getSourceValue() is None or \
   order.getDestinationValue() is None or \
   order.getSourceSectionValue() is None or \
   order.getDestinationSectionValue() is None or \
   order.getSourceDecisionValue() is None or \
   order.getDestinationDecisionValue() is None or \
   order.getSourceAdministrationValue() is None or \
   order.getDestinationAdministrationValue() is None or \
   order.getSourcePaymentValue() is None or \
   order.getDestinationPaymentValue() is None :

  if len(error_message) == 0 :
    error_message += 'Profil incomplet'
  else :
    error_message += ' - Profil incomplet'

# check if order is not empty
if order.getPortalType() == 'Purchase Order' :
  filter_dict = {'portal_type': 'Purchase Order Line'}
elif order.getPortalType() == 'Sales Order':
  filter_dict = {'portal_type': 'Sales Order Line'}
else :
  filter_dict = {'portal_type': 'Production Order Line'}
order_line_list = order.contentValues(filter=filter_dict)
if len(order_line_list)==0 :
  if len(error_message) == 0 :
    error_message += 'Commande vide'
  else :
    error_message += ' - Commande vide'
else :
  # check if each line is linked to a resource
  # and if variations are well defined
  for order_line in order_line_list :
    if order_line.getResourceValue() is None :
      if len(error_message) == 0 :
        error_message += 'Ligne sans produit'
      else :
        error_message += ' - Ligne sans produit'
      break
    if not order_line.getVariationBaseCategoryList() in (None, []) and not order_line.getVariationCategoryList() in (None, []) :
      if len(order_line.getVariationBaseCategoryList()) == 0 and len(order_line.getVariationCategoryList()) <> 0 :
        if len(error_message) == 0 :
          error_message += 'Variantes mal définies'
        else :
          error_message += ' - Variantes mal définies'
        break

return error_message
