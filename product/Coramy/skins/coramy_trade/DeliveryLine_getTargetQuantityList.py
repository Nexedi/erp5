## Script (Python) "DeliveryLine_getTargetQuantityList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=taille_list=[], coloris=None, morphologie=None
##title=
##
delivery_line = context
taille_list = taille_list
target_quantity_list = []

def category_property(category, property):
  if category <> None :
    if hasattr(category,property) :
      return getattr(category,property)
    else : 
      return " "
  else :
    return " "

for taille in taille_list :
  my_taille = 'taille/'+taille
  if coloris is not None and morphologie is not None :
    my_coloris = 'coloris/'+coloris
    my_morphologie = 'morphologie/'+morphologie
    if delivery_line.getCell(my_coloris, my_taille, my_morphologie, base_id='movement') <> None :
      target_quantity_list.append(delivery_line.getCell(my_coloris, my_taille, my_morphologie, base_id='movement').getProperty(key="target_quantity"))
    else :
      target_quantity_list.append(0)
  elif coloris is not None :
    my_coloris = 'coloris/'+coloris
    if delivery_line.getCell(my_coloris, my_taille, base_id='movement') <> None :
      target_quantity_list.append(delivery_line.getCell(my_coloris, my_taille, base_id='movement').getProperty(key="target_quantity"))
    else :
      target_quantity_list.append(0)

return target_quantity_list
