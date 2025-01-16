from DateTime import DateTime

translateString = context.Base_translateString
user_value = context.portal_membership.getAuthenticatedMember().getUserValue()

now = DateTime()

traceability_input_dict = {}
for traceability_input in context.Base_getExpectedTraceabilityInputList():
  traceability_input_reference = traceability_input.getReference()
  if traceability_input_reference not in traceability_input_dict:
    traceability_input_dict[traceability_input_reference] = []
  traceability_input_dict[traceability_input.getReference()].append(traceability_input)


data_dict = context.Base_generateValideTraceabilityDataDict(traceability_data)
unprocess_data_list = []
processed_data_list = []
already_used_dict = {}

for product_reference, serial_number_list in data_dict.iteritems():
  if product_reference in traceability_input_dict:
    traceability_input_list = traceability_input_dict[product_reference]

    length = min(len(traceability_input_list), len(serial_number_list))
    for index in range(length):
      serial_number = serial_number_list[index]
      serial_item = getattr(context.quality_assurance_module, serial_number, None)
      is_for_radio = False
      if serial_item:
        # check if can be reused
        affected_vin = serial_item.getAggregateValue(portal_type='VIN')

        # check if it's for radio
        traceability = serial_item.getFollowUpValue(portal_type='Traceability')
        if traceability:
          part_reference = traceability.getReference()
          part_product = context.portal_catalog.getResultValue(portal_type='Product', reference=part_reference)
          if part_product and part_product.getProductLine() == 'part/radio':
            is_for_radio = True
        if affected_vin and (not is_for_radio):
          already_used_dict[serial_number] = affected_vin.getReference()
          continue
      else:
        serial_item = context.quality_assurance_module.newContent(
          portal_type='Serial Number',
          id=serial_number,
          reference=serial_number
        )
        serial_item.validate()

      traceability_input = traceability_input_list[index]
      title = traceability_input.getTitle()
      if not " // " in title:
        title = '%s  // %s' % (title, serial_number)
      traceability_input.edit(
        effective_date = now,
        destination_decision_value = user_value,
        title = title
      )
      if is_for_radio:
        serial_item.setAggregateValueList(serial_item.getAggregateValueList(portal_type='VIN') + [context.getAggregateValue(portal_type='VIN')], portal_type='VIN')
        serial_item.setFollowUpValueList(serial_item.getFollowUpValueList(portal_type='Traceability') + [traceability_input], portal_type='Traceability')
      else:
        serial_item.setAggregateValue(context.getAggregateValue(portal_type='VIN'), portal_type='VIN')
        serial_item.setFollowUpValue(traceability_input, portal_type='Traceability')

      traceability_input.setAggregateValue(serial_item, portal_type='Serial Number')

      quality_me_line = traceability_input.getAggregateRelatedValue(portal_type='Manufacturing Execution Line')
      if quality_me_line:
        quality_me_line.edit(
          start_date = now,
          stop_date=now
        )
      traceability_input.post()
      processed_data_list.append(serial_number)
  else:
    for unprocess_number in serial_number_list:
      unprocess_number_value = getattr(context.quality_assurance_module, unprocess_number, None)
      if unprocess_number_value and unprocess_number_value.getAggregateReference(portal_type='VIN'):
        already_used_dict[unprocess_number] = unprocess_number_value.getAggregateReference(portal_type='VIN')
      else:
        unprocess_data_list.append(unprocess_number)

if unprocess_data_list:
  unprocess_data_list = list(set(unprocess_data_list))
  unprocess_data_list = [x for x in unprocess_data_list if x not in processed_data_list]

if unprocess_data_list or already_used_dict:
  if batch:
    return unprocess_data_list, already_used_dict
  msg = ''
  if unprocess_data_list:
    msg = msg + translateString("Those data are not processed")
  if already_used_dict:
    msg = msg + '\n' +  translateString("Already used:")
    for serial_number, vin in already_used_dict.iteritems():
      msg= msg + '\n' +  translateString(
        "${serial_number}:  ${vin}",
        mapping = {
          'serial_number' : serial_number,
          'vin': vin
        }
      )
  return context.Base_redirect('view_traceability_input', keep_items={
    'unprocess_data_list': unprocess_data_list,
    'portal_status_message': msg,
    'portal_status_level': 'error'})
return context.Base_redirect('view', keep_items={'portal_status_message': translateString("Data is posted")})
