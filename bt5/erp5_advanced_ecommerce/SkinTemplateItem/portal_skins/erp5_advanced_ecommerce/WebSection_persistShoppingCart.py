from DateTime import DateTime
import random

new_id = context.portal_ids.generateNewLengthId(
                     id_group="Sale_Order_Module-Sale_Order",
                     default=1)

random_min = 100000  # 9 digits
random_max = 1000000  # 10 digits
reference = "SO-%s-%s" % (new_id, random.randint(random_min,random_max))
shopping_cart.setReference(reference)

portal_type = shopping_cart.getPortalType()
module = context.getDefaultModule(portal_type)
sale_order = module.newContent(portal_type=portal_type,
                    reference=reference,
                    destination_value=person,
                    destination_section_value=person,
                    destination_decision_value=person,
                    start_date=DateTime(),
                    received_date=DateTime(),
                    comment=shopping_cart.getComment(),
                    # set trade condition
                    specialise=shopping_cart.getSpecialise())

for order_line in shopping_cart.contentValues(portal_type="Sale Order Line"):
  sale_order_line = sale_order.newContent(portal_type=order_line.getPortalType(),
                        resource=order_line.getResource(),
                        aggregate_list=order_line.getAggregateList(),
                        quantity=order_line.getQuantity(),
                        price=order_line.getPrice(),
                        title=order_line.getResourceTitle(),
                        variation=order_line.getVariation())
  resource_value = order_line.getResourceValue()
  base_category = resource_value.getVariationBaseCategory()
  #xxxxxxxxxxxxxxxxxxxx
  if base_category:
    getattr(sale_order_line,'set%s'%base_category.title())(getattr(order_line, 'get%s'%base_category.title())())

sale_order.Order_applyTradeCondition(shopping_cart.getSpecialiseValue())
sale_order.manage_setLocalRoles(person.Person_getUserId(), ['Auditor'])
return sale_order
