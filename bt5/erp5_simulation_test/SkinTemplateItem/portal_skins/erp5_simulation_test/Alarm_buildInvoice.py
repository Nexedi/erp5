# This script is a sample of alarm script that invokes builders.
# You may need to modify builder ID's according to your application.

portal = context.getPortalObject()
delivery_tool = portal.portal_deliveries

builder_id_list = (
  'purchase_invoice_builder',
  'purchase_invoice_transaction_trade_model_builder',
  'sale_invoice_builder',
  'sale_invoice_transaction_trade_model_builder',
)

for builder_id in builder_id_list:
  builder = getattr(delivery_tool, builder_id, None)
  if builder is None:
    continue
  delivery_portal_type = builder.getDeliveryPortalType()
  serialization_tag    = 'build:%s' % delivery_portal_type
  index_tag            = 'index:%s' % delivery_portal_type
  after_tag            = index_tag
  # depend on reindexing so that select methods
  # do not return movements that are already built
  after_method_id      = ('immediateReindexObject',
                          '_updateSimulation')
  activate_kw          = dict(tag=index_tag)
  builder.activate(
    limit=100,
    tag='invoice_builder_alarm',
    serialization_tag=serialization_tag,
    after_tag=after_tag,
    after_method_id=after_method_id).build(activate_kw=activate_kw)

# add a dummy activity so alarm calling can detect we still have a pending activity
# and do not start this script again before previous call is finished
context.activate(after_tag='invoice_builder_alarm').getId()
