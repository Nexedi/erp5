portal = context.getPortalObject()
delivery_tool = portal.portal_deliveries

builder_id_list = (
  'loyalty_transaction_builder',
)

for builder_id in builder_id_list:
  builder = getattr(delivery_tool, builder_id, None)
  if builder is None:
    continue
  delivery_portal_type = builder.getDeliveryPortalType()
  serialization_tag    = 'build:%s' % delivery_portal_type
  index_tag            = 'index:%s' % delivery_portal_type
  after_tag            = index_tag
  after_method_id      = ('recursiveImmediateReindexObject',
                          'immediateReindexObject',
                          'Delivery_updateAppliedRule')
  activate_kw          = dict(tag=index_tag)
  builder.activate(
    serialization_tag=serialization_tag,
    after_tag=after_tag,
    after_method_id=after_method_id).build(activate_kw=activate_kw)
