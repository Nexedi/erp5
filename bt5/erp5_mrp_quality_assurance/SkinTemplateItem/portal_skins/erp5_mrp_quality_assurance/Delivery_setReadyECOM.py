delivery = context

PO = delivery.getCausalityValue(portal_type='Production Order')
PPL = PO.getCausalityRelatedValue(portal_type='Production Packing List')
vin = delivery.getAggregateValue(portal_type='VIN')
PPL.setAggregateValue(vin, portal_type='VIN')
for line in PPL.objectValues(portal_type='Production Packing List Line'):
  line.setAggregateValue(vin, portal_type='VIN')

PPL.setReady()
return PPL
