# This script will check if a given reference exist in all checks.
# If this reference does not exist yet, we will have two choices
# 1 - if a end date is not passed yet, we will create the check
# 2 - if the end date is passed, we raise an error
from Products.ERP5Type.Message import Message
from Products.DCWorkflow.DCWorkflow import ValidationFailed

portal = context.getPortalObject()

if bank_account is None:
  if destination:
    bank_account = context.getDestinationPaymentValue()
  elif source:
    bank_account = context.getSourcePaymentValue()
  
if bank_account is None:
  msg = Message(domain='ui',message='Sorry, you must select an account')
  raise ValidationFailed(msg,)

if resource is None:
  msg = Message(domain='ui',message='Sorry, you must select a resource')
  raise ValidationFailed(msg,)

if reference is not None:
  reference_list = [reference]

elif reference_range_min is not None or reference_range_max is not None:
  reference_list = []

  if reference_range_max is None:
    reference_range_max = reference_range_min

  elif reference_range_min is None:
    reference_range_min = reference_range_max

  try:
    reference_range_min = int(reference_range_min)
    reference_range_max = int(reference_range_max)
  except ValueError:
    msg = Message(domain='ui', message='Sorry, make sure you have entered the right check number.')
    raise ValidationFailed(msg,)

  if reference_range_min>reference_range_max :
    msg = Message(domain='ui', message='Sorry, the min number must be less than the max number.')
    raise ValidationFailed(msg,)

  for ref in range(reference_range_min,reference_range_max+1):
    # We will look for each reference and add the right number
    reference_list.append("%07i" % ref)

check_list = []
bank_account_uid = bank_account.getUid()
resource_value = portal.restrictedTraverse(resource)
reference_dict = {}
# First we must parse everyting to make sure there is no error,
# this is safer because we catch Validation in workflow scripts
for check_reference in reference_list:
  message_tag = 'check_%s_%s_%s' % (resource, bank_account_uid, check_reference)
  # just raise an error.
  if context.portal_activities.countMessageWithTag(message_tag) != 0:
    msg = Message(domain='ui', message="There are operations pending that prevent to validate this document. Please try again later.")
    raise ValidationFailed(msg,)
  result = context.portal_catalog(portal_type = 'Check', reference = check_reference, 
                                  destination_payment_uid = bank_account.getUid(),
                                  default_resource_uid = resource_value.uid,
                                  simulation_state='!=deleted')
  result_len = len(result)
  if result_len == 0:
    if not context.Base_isAutomaticCheckCreationAllowed():
      msg = Message(domain = "ui", message="Sorry, the $type $reference for the account $account does not exist",
                                   mapping={'reference' : check_reference, 'account': bank_account.getInternalBankAccountNumber(),
                                            'type': resource_value.getTitle()})
      raise ValidationFailed(msg,)

  elif result_len > 1:
    msg = Message(domain = "ui", message="Sorry, the $type $reference for the account $account is duplicated",
                                   mapping={'reference' : reference, 'account': bank_account.getInternalBankAccountNumber(),
                                            'type': resource_value.getTitle()})
    raise ValidationFailed(msg,)

  reference_dict[check_reference] = {}
  reference_dict[check_reference]['result'] = result
  reference_dict[check_reference]['result_len'] = result_len
  reference_dict[check_reference]['message_tag'] = message_tag

for check_reference in reference_list:
  result_len = reference_dict[check_reference]['result_len']
  result = reference_dict[check_reference]['result']
  message_tag = reference_dict[check_reference]['message_tag']
  generic_model = None
  if result_len == 0:
    # This happens only if automatic creation is allowed. So create a new check at this point.
    # Get a checkbook for this bank account.
    checkbook = None
    if generic_model is None:
      composition_related_list = resource_value.getCompositionRelatedValueList()
      if len(composition_related_list) == 0:
        msg = Message(domain = "ui", message="Sorry, no checkbook model found")
        raise ValidationFailed(msg,)
      if len(composition_related_list) != 1:
        msg = Message(domain = "ui", message="Sorry, too many many checkbook model found")
        raise ValidationFailed(msg,)
      generic_model = composition_related_list[0]

    #generic_model = context.portal_catalog(portal_type = 'Checkbook Model', title = 'Generic')[0].getObject()
    # XXX it would be better to use a related key for this, but z_related_resource is too specific to
    # movement at the moment.
    for brain in context.portal_catalog(portal_type = 'Checkbook',
                                        title = 'Generic',
                                        destination_payment_uid = bank_account.getUid(),
                                        default_resource_uid = generic_model.getUid()):
      obj = brain.getObject()
      #if obj.getResourceUid() == generic_model.getUid():
      checkbook = obj
      #  break
    if checkbook is None:
      # Create a checkbook.
      # To prevent duplicated checkbooks for a single bank account, index this new checkbook immediately.
      # This has a performance penalty, but this part of the script will rarely be called (once per bank account).
      checkbook_tag = "checkbook_%s_%s" % (resource, bank_account_uid) 
      if context.portal_activities.countMessageWithTag(checkbook_tag) != 0:
        msg = Message(domain='ui', message="There are operations pending that prevent to validate this document. Please try again later.")
        raise ValidationFailed(msg,)
      checkbook = context.checkbook_module.newContent(portal_type = 'Checkbook',
                                                      title = 'Generic',
                                                      resource_value = generic_model,
                                                      destination_payment_value = bank_account,
                                                      activate_kw={'tag' : checkbook_tag} )
    # Create a check.
    check = checkbook.newContent(portal_type = 'Check', reference = check_reference, activate_kw={'tag': message_tag})
    # Automatically issue this check.
    check.confirm()
  else:
    check = result[0].getObject()
  check_list.append(check)

if reference is not None:
  return check_list[0]
return check_list
