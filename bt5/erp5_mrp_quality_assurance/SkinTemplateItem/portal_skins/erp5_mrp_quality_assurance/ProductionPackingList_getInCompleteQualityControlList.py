po = context.getCausalityValue(portal_type='Production Order')

me = po.ProductionOrder_getRelatedManufacturingExecutionDict()['parts_execution']

return me.Delivery_getNOKQualityControlList() + me.Delivery_getUpcomingQualityControlOperationList()
