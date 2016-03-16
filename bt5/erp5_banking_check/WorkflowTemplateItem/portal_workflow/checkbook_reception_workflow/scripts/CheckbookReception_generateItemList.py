from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

transaction = state_change['object']

# Check getBaobabSource and getBaobabDestination
transaction.Base_checkBaobabSourceAndDestination()

# Check that all lines do not define existing checks or checkbooks
transaction.CheckbookReception_checkOrCreateItemList(check=1)

# Start activities for each line
confirm_check = transaction.isImported()
transaction.CheckbookReception_checkOrCreateItemList(create=1,
                      confirm_check=confirm_check)


#from Products.DCWorkflow.DCWorkflow import ValidationFailed
#transaction = state_change['object']
#
## Check getBaobabSource and getBaobabDestination
#transaction.Base_checkBaobabSourceAndDestination()
#
#portal = transaction.getPortalObject()
#portal_activities = portal.portal_activities
#line_list = transaction.objectValues()
#encountered_check_identifiers_dict = {}
#
#def getReference(reference):
#  """
#    Convert a reference into an int.
#  """
#  # First convert to float to avoid failing to convert if reference = '1.0'
#  return int(float(reference))
#
#def generateReference(reference, original_reference):
#  """
#    Convert an int into a reference of correct length
#  """
#  reference = str(reference)
#  return '%s%s' % ('0' * (len(original_reference) - len(reference)), reference)
#
#def validateTravelerCheckReferenceFormat(traveler_check_reference):
#  """
#    Check provided traveler_check_reference format
#  """
#  if len(traveler_check_reference) != 10:
#    raise ValueError, 'Traveler check reference must be 10-char long.'
#  int(traveler_check_reference[4:])
#
#def getTravelerCheckReferenceNumber(traveler_check_reference):
#  """
#    Extract traveler check reference number
#  """
#  validateTravelerCheckReferenceFormat(traveler_check_reference)
#  return int(traveler_check_reference[4:])
#
#def getTravelerCheckReferencePrefix(traveler_check_reference):
#  """
#    Extract traveler check reference prefix
#  """
#  validateTravelerCheckReferenceFormat(traveler_check_reference)
#  return traveler_check_reference[:4]
#
#def generateTravelerCheckReference(number, original_traveler_check_reference):
#  """
#    Generate a traveler check reference from an existing reference (to
#    extract its prefix) and a new numerical value.
#  """
#  if not same_type(number, 0):
#    raise ValueError, 'Traveler check number must be only numeric.'
#  if len(str(number)) > 6:
#    raise ValueError, 'Traveler check number representation length must not exceed 6 char.'
#  prefix = getTravelerCheckReferencePrefix(original_traveler_check_reference)
#  return '%s%06d' % (prefix, number)
#
#def assertReferenceMatchListEmpty(match_list):
#  """
#    Check that the list is empty, otherwise gather all conflicting references and display them in the error message.
#    TODO: make the error message Localizer-friendly
#  """
#  if len(match_list) > 0:
#    matched_reference_list = []
#    for match in match_list:
#      matched_reference_list.append(match.getReference())
#    raise ValidationFailed, 'The following references are already allocated : %s' % (matched_reference_list, )
#
#def checkReferenceListUniqueness(reference_list, model, destination_payment_uid):
#  """
#    Check each given reference not to already exist.
#  """
#  if destination_payment_uid is None:
#    match_list = portal.portal_catalog(portal_type='Check', reference=reference_list, resource_relative_url=model)
#  else:
#    match_list = portal.portal_catalog(portal_type='Check', reference=reference_list, destination_payment_uid=destination_payment_uid, resource_relative_url=model)
#  assertReferenceMatchListEmpty(match_list)
#  for reference in reference_list:
#    tag = 'check_%s_%s_%s' % (model, destination_payment_uid, reference)
#    if encountered_check_identifiers_dict.has_key(tag) or portal_activities.countMessageWithTag(tag) != 0:
#      raise ValidationFailed, 'The following references are already allocated : %s' % ([reference, ], )
#
#def checkReferenceUniqueness(reference, model, destination_payment_uid):
#  """
#    Check the given reference not to already exist.
#  """
#  checkReferenceListUniqueness([reference, ], model, destination_payment_uid)
#
#start_date = transaction.getStartDate()
#destination = transaction.getDestination()
#
#for line in line_list:
#  quantity = line.getQuantity()
#  resource = line.getResourceValue()
#  reference_range_min = line.getReferenceRangeMin()
#
#  # We will look where we should create as many items
#  # as necessary and construct by the same time
#  # the aggregate list that we will store on the line
#  resource_portal_type = resource.getPortalType()
#  if resource_portal_type == 'Checkbook Model':
#    is_checkbook = True
#    module = portal.checkbook_module
#    model = resource.getComposition()
#    # XXX: portal_type value is hardcoded because I don't want to get the
#    # portaltype on each created object as it will always be the same.
#    # We need a method to get the default content portaltype on a Folder.
#    check_amount = line.getCheckAmount()
#    check_quantity = int(portal.restrictedTraverse(check_amount).getQuantity())
#    reference_to_int = getReference
#    int_to_reference = generateReference
#  else:
#    is_checkbook = False
#    module = portal.check_module
#    model = resource.getRelativeUrl()
#    # XXX: portal_type value is hardcoded, see XXX above.
#    if resource_portal_type == 'Check Model' and resource.isFixedPrice():
#      reference_to_int = getTravelerCheckReferenceNumber
#      int_to_reference = generateTravelerCheckReference
#    else:
#      reference_to_int = getReference
#      int_to_reference = generateReference
#
#  if resource.getAccountNumberEnabled():
#    destination_payment_value = line.getDestinationPaymentValue()
#    destination_payment_value.serialize()
#    destination_payment_uid = destination_payment_value.getUid()
#    destination_trade = line.getDestinationTrade()
#  else:
#    destination_payment_value = None
#    destination_payment_uid = None
#
#  aggregate_list = []
#  for i in xrange(quantity):
#    item = module.newContent()
#    item.setDestination(destination)
#    if destination_payment_value is not None:
#      item.setDestinationPaymentValue(destination_payment_value)
#      item.setDestinationTrade(destination_trade)
#    if is_checkbook:
#      last_reference_value = reference_to_int(reference_range_min) + check_quantity - 1
#      reference_list = [int_to_reference(x, reference_range_min) for x in range(reference_to_int(reference_range_min), last_reference_value + 1)]
#      checkReferenceListUniqueness(reference_list, model, destination_payment_uid)
#      reference_range_max = int_to_reference(last_reference_value, reference_range_min)
#      item.setReferenceRangeMax(reference_range_max)
#      item.setReferenceRangeMin(reference_range_min)
#      item.setResourceValue(resource)
#      item.setStartDate(start_date)
#      item.setTitle('%s - %s' % (reference_range_min, reference_range_max))
#      item.setCheckAmount(check_amount)
#      destination_section = item.getDestinationSection()
#      for j in reference_list:
#        tag = 'check_%s_%s_%s' % (model, destination_payment_uid, j)
#        encountered_check_identifiers_dict[tag] = None
#        check = item.newContent(portal_type='Check', title=j, activate_kw={'tag': tag})
#        check.setDestination(destination_section)
#        check.setStartDate(start_date)
#        check.setReference(j)
#        check.setResource(model)
#    else:
#      checkReferenceUniqueness(reference_range_min, model, destination_payment_uid)
#      item.setReference(reference_range_min)
#      item.setResource(model)
#      item.setTitle(reference_range_min)
#      if len(resource.objectValues()) > 0:
#        item_type = line.getCheckTypeValue()
#        item.setPrice(item_type.getPrice())
#        item.setPriceCurrency(line.getPriceCurrency())
#      last_reference_value = reference_to_int(reference_range_min)
#      tag = 'check_%s_%s_%s' % (model, destination_payment_uid, reference_range_min)
#      encountered_check_identifiers_dict[tag] = None
#      # Trigger a dummy activity just to avoi dbeing able to create that check multiple times in the same checkbook reception
#      item.activate(tag=tag).getUid()
#    # update reference_range_min for the next pass
#    reference_range_min = int_to_reference(last_reference_value + 1, reference_range_min)
#    # I (seb) think this is a big mistake
#    #if item.getPortalType()=='Check':
#    #  portal.portal_workflow.doActionFor(item,'confirm_action',
#    #                                     wf_id='check_workflow')
#    aggregate_list.append(item)
#
#  # Finally set the aggregate list on the line
#  line.setAggregateValueList(aggregate_list)
