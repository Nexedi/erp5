## Script (Python) "sample_delivery_count_samples"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
sample_delivery = context
lignes_cde = sample_delivery.contentValues(filter={'portal_type':'Delivery Line'})
total = 0

for ligne in lignes_cde:
  total += ligne.getQuantity()

return total
