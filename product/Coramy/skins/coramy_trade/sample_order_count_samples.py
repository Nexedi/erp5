## Script (Python) "sample_order_count_samples"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
sample_order = context
lignes_cde = sample_order.contentValues(filter={'portal_type':'Sample Order Line'})
total = 0

for ligne in lignes_cde:
  total += ligne.getQuantity()

return total
