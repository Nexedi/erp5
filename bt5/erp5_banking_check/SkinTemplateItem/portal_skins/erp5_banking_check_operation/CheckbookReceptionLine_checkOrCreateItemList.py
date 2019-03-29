from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message
checkbook_reception = context.getParentValue()

portal = checkbook_reception.getPortalObject()
portal_activities = portal.portal_activities
if encountered_check_identifiers_dict is None:
  encountered_check_identifiers_dict = {}

def getReference(reference):
  """
    Convert a reference into an int.
  """
  # First convert to float to avoid failing to convert if reference = '1.0'
  return int(float(reference))

def generateReference(reference, original_reference):
  """
    Convert an int into a reference of correct length
  """
  reference = str(reference)
  return '%s%s' % ('0' * (len(original_reference) - len(reference)), reference)

def validateTravelerCheckReferenceFormat(traveler_check_reference):
  """
    Check provided traveler_check_reference format
  """
  if len(traveler_check_reference) != 10:
    message = Message(domain='ui', message='Traveler check reference must be 10-char long.')
    raise ValueError(message,)
  int(traveler_check_reference[4:])

def getTravelerCheckReferenceNumber(traveler_check_reference):
  """
    Extract traveler check reference number
  """
  validateTravelerCheckReferenceFormat(traveler_check_reference)
  return int(traveler_check_reference[4:])

def getTravelerCheckReferencePrefix(traveler_check_reference):
  """
    Extract traveler check reference prefix
  """
  validateTravelerCheckReferenceFormat(traveler_check_reference)
  return traveler_check_reference[:4]

def generateTravelerCheckReference(number, original_traveler_check_reference):
  """
    Generate a traveler check reference from an existing reference (to
    extract its prefix) and a new numerical value.
  """
  if not same_type(number, 0):
    message = Message(domain='ui', message='Traveler check number must be only numeric.')
    raise ValueError(message,)
  if len(str(number)) > 6:
    message = Message(domain='ui', message='Traveler check number representation length must not exceed 6 char.')
    raise ValueError(message,)
  prefix = getTravelerCheckReferencePrefix(original_traveler_check_reference)
  return '%s%06d' % (prefix, number)

def assertReferenceMatchListEmpty(match_list, internal_bank_account_number):
  """
    Check that the list is empty, otherwise gather all conflicting references and display them in the error message.
    TODO: make the error message Localizer-friendly
  """
  if len(match_list) > 0:
    matched_reference_list = []
    for match in match_list:
      matched_reference_list.append('%s (%s)' % (match.getReference(), internal_bank_account_number))
    message = Message(domain='ui', message='The following references are already allocated : $reference_list',
                      mapping={'reference_list': matched_reference_list})
    raise ValidationFailed(message,)

def checkReferenceListUniqueness(reference_list, model_uid, destination_payment_value, unique_per_account):
  """
    Check each given reference not to already exist.
  """
  catalog_kw = dict(
      portal_type='Check',
      reference=reference_list,
      simulation_state='!=deleted',
      default_resource_uid=model_uid,
  )
  if destination_payment_value is None:
    destination_payment_uid = None
    internal_bank_account_number = None
  else:
    destination_payment_uid = destination_payment_value.getUid()
    internal_bank_account_number = destination_payment_value.getInternalBankAccountNumber()
    # unique_per_account is True  -> references are unique per account
    # unique_per_account is False -> references are unique per country
    if unique_per_account:
      catalog_kw['destination_payment_uid'] = destination_payment_uid
    else:
      reference_match = "%s%%" % (destination_payment_value.getReference()[:2], )
      catalog_kw['baobab_destination_payment_reference'] = reference_match
  match_list = portal.portal_catalog(**catalog_kw)
  assertReferenceMatchListEmpty(match_list, internal_bank_account_number)
  for reference in reference_list:
    tag = 'check_%s_%s_%s' % (model_uid, destination_payment_uid, reference)
    if encountered_check_identifiers_dict.has_key(tag):
      message = Message(domain='ui', message='The following references are already allocated : $reference_list',
                        mapping={'reference_list': ['%s (%s)' % (reference, internal_bank_account_number) ]})
      raise ValidationFailed(message,)
    encountered_check_identifiers_dict[tag] = None

start_date = checkbook_reception.getStartDate()
destination = checkbook_reception.getDestination()

line = context
quantity = line.getQuantity()
resource = line.getResourceValue()
reference_range_min = line.getReferenceRangeMin()

# We will look where we should create as many items
# as necessary and construct by the same time
# the aggregate list that we will store on the line
resource_portal_type = resource.getPortalType()
if resource_portal_type == 'Checkbook Model':
  is_checkbook = True
  module = portal.checkbook_module
  model_value = resource.getCompositionValue()
  model = resource.getComposition()
  model_uid = model_value.getUid()
  # XXX: portal_type value is hardcoded because I don't want to get the
  # portaltype on each created object as it will always be the same.
  # We need a method to get the default content portaltype on a Folder.
  check_amount = line.getCheckAmount()
  check_quantity = int(portal.restrictedTraverse(check_amount).getQuantity())
  reference_to_int = getReference
  int_to_reference = generateReference
else:
  is_checkbook = False
  module = portal.check_module
  model = resource.getRelativeUrl()
  model_uid = resource.getUid()
  # XXX: portal_type value is hardcoded, see XXX above.
  if resource_portal_type == 'Check Model' and resource.isFixedPrice():
    reference_to_int = getTravelerCheckReferenceNumber
    int_to_reference = generateTravelerCheckReference
  else:
    reference_to_int = getReference
    int_to_reference = generateReference

if resource.getAccountNumberEnabled():
  destination_payment_value = line.getDestinationPaymentValue()
  # Not required any more to serialize the bank account
  #destination_payment_value.serialize()
  context.log('context.getRelativeUrl() before getUid of destination payment', context.getRelativeUrl())
  if destination_payment_value is None:
    message = Message(domain='ui', message='There is not destination payment on line with id: $id', mapping={'id': context.getId()})
    raise ValueError(message,)
  destination_trade = line.getDestinationTrade()
else:
  destination_payment_value = None

unique_per_account = resource.isUniquePerAccount()
aggregate_list = []
for i in xrange(int(quantity)):
  if create == 1:
    item = module.newContent(activate_kw={'tag': tag, 'priority':4})
    context.log('New Item created with Id', item.getId())
    item.setDestination(destination)
    if destination_payment_value is not None:
      item.setDestinationPaymentValue(destination_payment_value)
      item.setDestinationTrade(destination_trade)
  if is_checkbook:
    last_reference_value = reference_to_int(reference_range_min) + check_quantity - 1
    reference_list = [int_to_reference(x, reference_range_min) for x in range(reference_to_int(reference_range_min), last_reference_value + 1)]
    reference_range_max = int_to_reference(last_reference_value, reference_range_min)
    if check == 1:
      checkReferenceListUniqueness(reference_list, model_uid, destination_payment_value, unique_per_account)
    if create == 1:
      item.setReferenceRangeMax(reference_range_max)
      item.setReferenceRangeMin(reference_range_min)
      item.setResourceValue(resource)
      item.setStartDate(start_date)
      item.setTitle('%s - %s' % (reference_range_min, reference_range_max))
      item.setCheckAmount(check_amount)
      destination_section = item.getDestinationSection()
      if confirm_check:
        item.confirm()
      for j in reference_list:
        #encountered_check_identifiers_dict[tag] = None
        check = item.newContent(portal_type='Check', title=j, activate_kw={'tag': tag, 'priority':4})
        context.log('New Sub Item created with Id', check.getId())
        check.setDestination(destination_section)
        check.setStartDate(start_date)
        check.setReference(j)
        check.setResource(model)
        if confirm_check:
          check.confirm()
  else:
    last_reference_value = reference_to_int(reference_range_min)
    if check == 1:
      checkReferenceListUniqueness([reference_range_min, ], model_uid, destination_payment_value, unique_per_account)
    if create == 1:
      item.setReference(reference_range_min)
      item.setResource(model)
      item.setTitle(reference_range_min)
      if len(resource.objectValues()) > 0:
        item_type = line.getCheckTypeValue()
        item.setPrice(item_type.getPrice())
        item.setPriceCurrency(line.getPriceCurrency())
      if confirm_check:
        item.setStartDate(start_date)
        item.confirm()
      #encountered_check_identifiers_dict[tag] = None
  # update reference_range_min for the next pass
  reference_range_min = int_to_reference(last_reference_value + 1, reference_range_min)
  # I (seb) think this is a big mistake
  #if item.getPortalType()=='Check':
  #  portal.portal_workflow.doActionFor(item,'confirm_action',
  #                                     wf_id='check_workflow')
  if create == 1:
    aggregate_list.append(item)

# Finally set the aggregate list on the line
if create == 1:
  line.setAggregateValueList(aggregate_list)

return encountered_check_identifiers_dict
