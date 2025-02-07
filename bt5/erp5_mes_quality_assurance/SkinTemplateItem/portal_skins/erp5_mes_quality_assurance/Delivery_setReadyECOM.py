delivery = context

production_type = context.Base_getProductionType()

PO = delivery.getCausalityValue(portal_type='Production Order')
PPL = PO.getCausalityRelatedValue(portal_type='Production Packing List')
production_object = delivery.getAggregateValue(portal_type=production_type)
PPL.setAggregateValue(production_object, portal_type=production_type)
for line in PPL.objectValues(portal_type='Production Packing List Line'):
  line.setAggregateValue(production_object, portal_type=production_type)

PPL.setReady()
return PPL
