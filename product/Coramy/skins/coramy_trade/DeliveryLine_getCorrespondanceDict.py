## Script (Python) "DeliveryLine_getCorrespondanceDict"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
delivery_line = context
correspondance_dict = {}

if delivery_line.hasCellContent() :
  variation_base_category_list = delivery_line.getVariationBaseCategoryList()
  for base_category in variation_base_category_list :
    correspondance_dict[base_category] = {}
  for cell in delivery_line.contentValues(filter={'portal_type' : ['Delivery Cell', 'Invoice Cell']}) :
    if 'coloris' in variation_base_category_list :
      correspondance_dict['coloris']['coloris/'+cell.getColoris()] = cell.Amount_getColorisClient()
    if 'taille' in variation_base_category_list :
      if 'morphologie' in variation_base_category_list :
        correspondance_dict['taille']['taille/'+cell.getTaille()+'morphologie/'+cell.getMorphologie()] = cell.Amount_getTailleClient()
      else :
        correspondance_dict['taille']['taille/'+cell.getTaille()] = cell.Amount_getTailleClient()
    if 'morphologie' in variation_base_category_list :
      correspondance_dict['morphologie']['morphologie/'+cell.getMorphologie()] = cell.getMorphologieValue().getMorphoTypeTitle()

return correspondance_dict
