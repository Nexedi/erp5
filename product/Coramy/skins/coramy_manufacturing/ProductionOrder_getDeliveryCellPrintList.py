## Script (Python) "ProductionOrder_getDeliveryCellPrintList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
order_line = context
resource = order_line.getResourceValue()
movement_list = []
pretty_list = []

if resource <> None :

  if order_line.hasCellContent() :
    raw_movement_list = order_line.contentValues(filter={'portal_type':'Delivery Cell'})
    movement_list = order_line.sort_object_list(unordered_list=raw_movement_list, sort_order = (('variation_text', 'ASC'),))
  else :
    movement_list.append(order_line)

  for movement in movement_list :

    my_variation_base_category_list = movement.getVariationBaseCategoryList()
    if 'coloris' in my_variation_base_category_list :
      if len(movement.getColorisValueList()) > 0 :
        coloris_object = movement.getColorisValueList()[0]
      else :
        coloris_object = None
    else :
      coloris_object = None
    if 'morphologie' in my_variation_base_category_list :
      if len(movement.getMorphologieValueList()) > 0 :
        morphologie_object = movement.getMorphologieValueList()[0]
      else :
        morphologie_object = None
    else :
      morphologie_object = None

    line_resource = resource.getId()
#    line_designation = resource.getDescription()
    if movement.getColoris() is not None :
      line_coloris = ['coloris/'+movement.getColoris()]
    else :
      line_coloris = []
    if movement.getTaille() is not None :
      line_taille = ['taille/'+movement.getTaille()]
    else :
      line_taille = []
    if movement.getMorphologie() is not None :
      line_morphologie = ['morphologie/'+movement.getMorphologie()]
    else :
      line_morphologie = []
    variation_list = line_coloris + line_morphologie + line_taille

    if morphologie_object is not None :
      corresp_variation_list = [movement.getTaille()]+[morphologie_object.getMorphoType()]
    else :
      corresp_variation_list = [movement.getTaille()]+['value']

    # find taille_client
    line_taille_client = ' '
    correspondance_list = resource.getSpecialiseValueList(portal_type='Correspondance Tailles')
    if len(correspondance_list) == 1 :
      my_correspondance = correspondance_list[0]
      mapped_value_list = my_correspondance.objectValues()
      for mapped_value in mapped_value_list :
        if mapped_value.test(my_correspondance.asContext(categories=corresp_variation_list)) :
          line_taille_client = mapped_value.getProperty(key='taille_client')
          break

    try :
     line_quantity = float(movement.getProperty(key='quantity'))
    except :
     line_quantity = 0

    line_date = order_line.aq_parent.getStopDate()

    # find code_article
    line_code_article = ''
    variated_reference_list = resource.contentValues(filter={'portal_type':'Variated Reference'})
    # we search a variated_reference wich define 'code_article'
    my_variated_reference = None
    for variated_reference in variated_reference_list :
      if len(variated_reference.getMappedValuePropertyList()) <> 0 :
        if variated_reference.getMappedValuePropertyList()[0] == 'code_article' :
          my_variated_reference = variated_reference
          break
    if my_variated_reference is not None :
      mapped_value_list = my_variated_reference.objectValues()
      for mapped_value in mapped_value_list :
        if mapped_value.test(my_variated_reference.asContext(categories=variation_list)) :
          line_code_article = mapped_value.getProperty(key='code_article')
          break

    line_items = [line_resource,line_coloris,line_morphologie,line_taille,
                  line_taille_client,line_quantity,line_date,line_code_article]
    pretty_list.append(line_items)

return pretty_list
