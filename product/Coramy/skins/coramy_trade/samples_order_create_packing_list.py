## Script (Python) "samples_order_create_packing_list"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
#request = context.REQUEST
#response = request.RESPONSE
delivery_module = context.getPortalObject().livraison_echantillon
delivery_type = 'Samples Packing List'
delivery_line_type = 'Delivery Line'
order_line_type = 'Sample Order Line'

# Create a new packing list
order = context.getObject()
new_id = str(delivery_module.generateNewId())
context.portal_types.constructContent(type_name=delivery_type,
        container=delivery_module,
        id=new_id,
        order_id=order.getId(),
        title = order.getTitle(),
        target_start_date = order.getStartDate(),
        target_stop_date = order.getStopDate(),
       )
delivery = delivery_module[new_id]


# delivery.edit(
#         source = order.getSource(),
#         destination = order.getDestination(),
#         causality_reference = order
# )

# Create each line
for order_line in context.contentValues(filter={'portal_type':order_line_type}):
  order_line_object = order_line.getObject()
  if order_line_object is not None:
    new_id = order_line_object.getId()
    context.portal_types.constructContent(type_name=delivery_line_type,
        container=delivery,
        id=new_id,
        title = order_line_object.getTitle(),
        description = order_line_object.getDescription(),
        quantity = order_line_object.getQuantity(),
        target_quantity = order_line_object.getQuantity(),
        target_start_date = order.getStartDate(),
        target_stop_date = order.getStopDate(),
        resource = order_line_object.getResource(),
        quantity_unit = order_line_object.getQuantityUnit()
     )
    delivery[new_id].setVariationCategoryList(order_line_object.getVariationCategoryList())

# If we do this before, each added line will take 20 times more time
# because of programmable acquisition
delivery.edit(
        source = order.getSource(),
        destination = order.getDestination(),
        causality_value = order
)

return delivery
