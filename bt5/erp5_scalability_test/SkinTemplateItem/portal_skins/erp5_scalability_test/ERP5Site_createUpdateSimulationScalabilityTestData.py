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
  sale_order.activate(tag='confirm_order').confirm()
  return sale_order

for _ in range(order_count):
  makeSaleOrder()

tag = 'build_packing_list'
portal.portal_alarms.invoice_builder_alarm.activate(
    tag=tag,
    after_tag='confirm_order',
).activeSense()


for i in range(expand_count):
  next_tag = 'expand_%s' % i
  portal.portal_catalog.activate(
      tag=next_tag,
      after_tag=tag,
      activity='SQLQueue',
      priority=5,
  ).searchAndActivate(
      portal_type='Sale Order',
      method_id='updateSimulation',
      method_kw={'expand_root': 1, 'index_related': 1}, # XXX do we need index_related
      packet_size=1,
      activate_kw={
        'priority': 4,
        'tag': next_tag,
        'after_method_id': (
            "_updateSimulation",
            "immediateReindexObject",
            "recursiveImmediateReindexObject")
      },
  )
  tag = next_tag

container.REQUEST.RESPONSE.setStatus(200)
return "Done"
