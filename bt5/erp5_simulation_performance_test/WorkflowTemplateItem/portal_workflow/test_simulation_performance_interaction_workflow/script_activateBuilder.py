# mostly copied & pasted from Alarm_buildPackingList

delivery = state_change['object']
builder = delivery.getPortalObject().portal_deliveries[{
  'Sale Order': 'test_sale_packing_list_builder',
  'Sale Packing List': 'test_sale_invoice_builder',
}[delivery.getPortalType()]]
delivery_portal_type = builder.getDeliveryPortalType()
serialization_tag    = 'build:' + delivery_portal_type
index_tag            = 'index:' + delivery_portal_type
after_method_id      = ('immediateReindexObject',
                        'expand',
                        '_updateSimulation')
activate_kw          = dict(tag=index_tag)
builder.activate(
  serialization_tag=serialization_tag,
  after_tag=index_tag,
  after_method_id=after_method_id).build(activate_kw=activate_kw)
