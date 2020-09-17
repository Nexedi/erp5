"""Create test data for updateSimulation scalability test.
"""
import random
rng = random.Random(random_seed)

if not hasattr(rng, 'randint'):
  # XXX if we don't have ERP5 patch which allow random.Random
  rng = random

portal = context.getPortalObject()

sale_trade_condition, = portal.portal_catalog(
    portal_type="Sale Trade Condition",
    reference='STC-General',
)
sale_trade_condition = sale_trade_condition.getObject()

resources = []
for _ in range(10):
  resource = portal.product_module.newContent(
      title='Scalability Test Resource %s' % (rng.randint(0, 10000)),
  )
  resource.validate()
  resources.append(resource)

customers = []
for _ in range(10):
  customer = portal.organisation_module.newContent(
      title='Scalability Test Organisation %s' % (rng.randint(0, 10000)),
  )
  customer.validate()
  customers.append(customer)


def makeSaleOrder():
  sale_order = portal.sale_order_module.newContent(
      portal_type='Sale Order',
      title='Scalability Test Sale Order %s' % (rng.randrange(10000)),
      start_date=DateTime() + (rng.random() * 100.),
      specialise_value=sale_trade_condition,
  )
  sale_order.setDestinationSectionValue(rng.choice(customers))
  sale_order.setDestinationValue(rng.choice(customers))
  sale_order.SaleOrder_applySaleTradeCondition()
  for i in range(rng.randint(1, 10)):
    sale_order.newContent(
        portal_type='Sale Order Line',
        int_index=i,
        resource_value=rng.choice(resources),
        quantity=rng.random() * 20,
        price=rng.random() * 100,
    )
  sale_order.Base_checkConsistency()
  sale_order.activate().confirm()
  return sale_order

for _ in range(order_count):
  makeSaleOrder()

for _ in range(expand_count):
  context.portal_catalog.activate(
      activity='SQLQueue',
      queue='SQLQueue',
      priority=5,
  ).searchAndActivate(
      portal_type='Sale Order',
      method_id='updateSimulation',
      method_kw={'expand_root': 1, 'index_related': 1}
  )

container.REQUEST.RESPONSE.setStatus(200)
return "Done"
