"""
  This script were copied from erp5_simulation_test, and it must be
  improved/adapted for configurator purpose.
"""

# This script is a sample of alarm script that invokes builders.
# You may need to modify builder ID's according to your application.

portal = context.getPortalObject()
delivery_tool = portal.portal_deliveries

builder_id_list = (
  'internal_packing_list_builder',
  'sale_packing_list_builder',
  'purchase_packing_list_builder',
)

for builder_id in builder_id_list:
  builder = getattr(delivery_tool, builder_id, None)
  if builder is None:
    continue
  if portal.portal_activities.countMessage(
      method_id='build',
      path=builder.getPath(), ):
    continue

  delivery_portal_type = builder.getDeliveryPortalType()
  serialization_tag    = 'build:%s' % delivery_portal_type
  index_tag            = 'index:%s' % delivery_portal_type
  after_tag            = index_tag
  # depend on reindexing so that select methods
  # do not return movements that are already built
  after_method_id      = ('recursiveImmediateReindexObject',
                          'immediateReindexObject',
                          '_updateSimulation')
  activate_kw          = dict(tag=index_tag)
  builder.activate(
    limit=100,
    serialization_tag=serialization_tag,
    after_tag=after_tag,
    after_method_id=after_method_id).build(activate_kw=activate_kw)
