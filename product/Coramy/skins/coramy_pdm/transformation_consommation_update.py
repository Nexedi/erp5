## Script (Python) "transformation_consommation_update"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=reference_taille, quantity, form_id
##title=
##
l_items = context.getQLineItemList()
l_items = map(lambda x: x[0], l_items)
c_items = context.getQColumnItemList()
c_items = map(lambda x: x[0], c_items)
grille = context.getDefaultValue('specialise', portal_type=('Grille Consommation',))
request = context.REQUEST
quantity = float(quantity)

for i in l_items:
  for j in c_items:
    try:
      cell = grille.getCell(reference_taille[7:], j[7:], base_id='quantity')
      if cell is None:
        return "Erreur à signaler à TB/JPS %s %s %s:" % (grille.getUrl(), reference_taille[7:], j[7:])
      default_quantity = float(cell.quantity)
    except:
      default_quantity = None
    if default_quantity is not None:
      cell = context.newCell(i, j, base_id='quantity')
      new_quantity = default_quantity * quantity
      cell.edit(mapped_value_property_list = ['quantity'],
                quantity = new_quantity, force_update=1)
    else:
      cell = context.newCell(i, j, base_id='quantity')
      cell.edit(mapped_value_property_list = ['quantity'],
                quantity = 99999.999)

# Required to set Mapped Value Parameters
# This is a bit simple but it works
# Another method consists in setting by hand each cell, but that is a bit
# like repeating the same code again and again
context.fixConsistency()

redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , form_id
                              , 'portal_status_message=Grille+Consommation+Updated.'
                              )
return request[ 'RESPONSE' ].redirect( redirect_url )
