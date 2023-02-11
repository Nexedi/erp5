"""Create test data for sales order / sales packing list build benchmark.
"""
import random

rng = random.Random(random_seed)

portal = context.getPortalObject()

sale_trade_condition, = portal.portal_catalog(
  portal_type="Sale Trade Condition",
  reference='STC-General',
)
sale_trade_condition = sale_trade_condition.getObject()

resources = []
for _ in range(10):
  resource = portal.product_module.newContent(
    title='Scalability Test Resource %s %s' %
    (random_seed, rng.randint(0, 10000)), )
  resource.validate()
  resources.append(resource)

customers = []
for _ in range(10):
  customer = portal.organisation_module.newContent(
    title='Scalability Test Organisation %s %s' %
    (random_seed, rng.randint(0, 10000)), )
  customer.validate()
  customers.append(customer)


def makeSaleOrder():
  sale_order = portal.sale_order_module.newContent(
    portal_type='Sale Order',
    title='Scalability Test Sale Order %s %s' %
    (random_seed, rng.randrange(10000)),
    start_date=DateTime() + (rng.random() * 100.),
    specialise_value=sale_trade_condition,
  )
  # note: we use "edit" to have multiple entries in edit_workflow, like when
  # a real user inputs data.
  sale_order.edit(stop_date=sale_order.getStopDate() + (rng.random() * 100.))
  sale_order.edit(destination_section_value=rng.choice(customers))
  sale_order.edit(destination_value=rng.choice(customers))
  sale_order.SaleOrder_applySaleTradeCondition()
  for i in range(rng.randint(1, 10)):
    sale_order.newContent(
      portal_type='Sale Order Line',
      resource_value=rng.choice(resources),
      quantity=1 + rng.random() * 20,
      price=rng.random() * 100,
    ).edit(
      int_index=i, )
  sale_order.Base_checkConsistency()
  sale_order.confirm()
  return sale_order


for _ in range(order_count):
  order = makeSaleOrder()
  # build packing lists one by one, because we create a lot and don't want the
  # global builder to try to build them all in one big transaction
  expand_tag = 'build:%s' % order.getPath()
  order.reindexObject(activate_kw={'tag': expand_tag})
  portal.portal_deliveries.sale_packing_list_builder.activate(
    activity='SQLQueue',
    after_tag=expand_tag,
  ).build(explanation_uid=order.getUid())

# cancel packing lists, so that they are not selected by
# DeliveryBuilder_selectConfirmedDeliveryList
portal.portal_catalog.searchAndActivate(
  portal_type='Sale Packing List',
  simulation_state='confirmed',
  method_id='SalePackingList_tryToCancel',
)

# undo redirect from SaleOrder_applySaleTradeCondition
container.REQUEST.RESPONSE.setStatus(200)
return "Done"
