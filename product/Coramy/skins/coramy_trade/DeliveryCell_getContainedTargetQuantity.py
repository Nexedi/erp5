## Script (Python) "DeliveryCell_getContainedTargetQuantity"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
delivery_cell = context

if delivery_cell.getPortalType() in ('Sales Packing List Line', 'Purchase Packing List Line') :
  delivery_uid = delivery_cell.aq_parent.getUid()
else :
# we are on a Delivery Cell
  delivery_uid = delivery_cell.aq_parent.aq_parent.getUid()

resource_uid = delivery_cell.getResourceValue().getUid()
variation_text = delivery_cell.getVariationText()

sql_list = delivery_cell.DeliveryCell_zGetContainedTargetQuantity(delivery_uid=delivery_uid,resource_uid=resource_uid,variation_text=variation_text)

if len(sql_list)>0 :
  if sql_list[0].target_quantity is not None :
    return float(sql_list[0].target_quantity)
  else :
    return 0
else :
  return 0
