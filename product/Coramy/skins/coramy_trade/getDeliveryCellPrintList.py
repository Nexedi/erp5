## Script (Python) "getDeliveryCellPrintList"
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
    movement_list = order_line.contentValues(filter={'portal_type':'Delivery Cell'})
  else :
    movement_list.append(order_line)

  for movement in movement_list :

    my_variation_base_category_list = movement.getVariationBaseCategoryList()
    if 'coloris' in my_variation_base_category_list :
      if len(movement.getColorisValueList()) > 0 :
        variante_object = movement.getColorisValueList()[0]
      else :
        variante_object = None
    elif 'variante' in my_variation_base_category_list :
      if len(movement.getVarianteValue()) > 0 :
        variante_object = movement.getVarianteValueList()[0]
      else :
        variante_object = None
    else :
      variante_object = None

    if variante_object <> None:
      if variante_object.getSourceReference() in (None, '', 'None'):
        line_source_reference = resource.getSourceReference()
      else :
        if resource.getSourceReference() in (None, '', 'None'):
          line_source_reference = variante_object.getSourceReference()
        else:
          line_source_reference = "%s %s" % (resource.getSourceReference(), variante_object.getSourceReference())
    else :
      line_source_reference = resource.getSourceReference()

    line_resource = resource.getId()
    line_designation = resource.getDescription()
    line_variantes = movement.getVariationCategoryList()
    try :
     if order_line.getPortalType() == 'Production Packing List Line' :
       line_quantity = float(movement.getProperty(key='target_quantity'))
     else :
       line_quantity = float(movement.getProperty(key='quantity'))
    except :
     line_quantity = 0
    try :
     line_price = float(movement.getProperty(key='price'))
    except :
     line_price = 0

    if order_line.getQuantityUnit() <> None :
      unit_items = order_line.getQuantityUnit().split('/')
      line_unit = unit_items[len(unit_items)-1]
    else :
      line_unit = ''

    line_date = order_line.aq_parent.getTargetStartDate()

    line_total = line_quantity*line_price

    if resource.getPortalType() == 'Composant' :
      line_type = resource.getTypeComposant()
    elif resource.getPortalType() == 'Tissu' :
      line_type = resource.getMotif()
    else :
      line_type = ' '

    try :
      line_source = resource.getSourceTitle()
    except :
      line_source = ' '

    line_items = [line_source_reference,line_resource,line_designation,line_variantes,line_quantity,line_unit,line_price,line_total,line_date,line_type,line_source]
    pretty_list.append(line_items)

return pretty_list
