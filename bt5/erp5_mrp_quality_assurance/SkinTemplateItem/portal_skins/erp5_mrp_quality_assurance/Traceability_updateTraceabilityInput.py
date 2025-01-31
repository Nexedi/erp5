clone_one = context.getFollowUpRelatedValue(portal_type='Traceability')
if clone_one:
  return clone_one.Base_redirect('view')

# set serial number's production object to None, so it can be reused
serial_number = context.getAggregateValue(portal_type='Serial Number')

production_type = context.Base_getProductionType()

is_for_radio = False
part_reference = context.getReference()
part_product = context.portal_catalog.getResultValue(portal_type='Product', reference=part_reference)
if part_product and part_product.getProductLine() == 'part/radio':
  is_for_radio = True

if is_for_radio:
  actually_production_object = context.getAggregateValue(portal_type=production_type)
  if actually_production_object:
    new_aggregate_production_object_list = [x for x in serial_number.getAggregateValueList(portal_type=production_type) if x.getRelativeUrl() != actually_production_object.getRelativeUrl()]
    serial_number.setAggregateValueList(new_aggregate_production_object_list, portal_type=production_type)

  new_follow_up_traceability_list = [x for x in serial_number.getFollowUpValueList(portal_type='Traceability') if x.getRelativeUrl() != context.getRelativeUrl()]
  serial_number.setFollowUpValueList(new_follow_up_traceability_list, portal_type='Traceability')



else:
  serial_number.setAggregateValue(None, portal_type=production_type)
  serial_number.setFollowUpValue(None, portal_type='Traceability')




clone_one = context.Base_createCloneDocument(batch_mode=True)
clone_one.setFollowUpValueList(clone_one.getFollowUpValueList(portal_type='Manufacturing Execution Line') + [context])
clone_one.setDestinationDecisionValue(None)
clone_one.setTitle(clone_one.getTitle().split('//')[0])

me_line = context.getAggregateRelatedValue(portal_type='Manufacturing Execution Line')
clone_line = me_line.Base_createCloneDocument(batch_mode=True)
clone_line.setAggregateValue(clone_one)

clone_one.plan()
clone_one.confirm()

return clone_one.Base_redirect('view')
