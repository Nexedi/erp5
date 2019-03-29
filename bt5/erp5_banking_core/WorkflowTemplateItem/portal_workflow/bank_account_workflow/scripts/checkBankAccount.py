from Products.ERP5Type.Message import Message
from Products.DCWorkflow.DCWorkflow import ValidationFailed

bank_account = state_change['object']

# use of the constraint
if bank_account.getParentValue().getPortalType()!= 'Person':
  vliste = bank_account.checkConsistency()
  if len(vliste) != 0:
    raise ValidationFailed(vliste[0].getTranslatedMessage(),)

if bank_account.getParentValue().getPortalType()== 'Person':
  # Can't have two bank account
  for obj in bank_account.getParentValue().objectValues():
    if obj.getPortalType() == "Bank Account" and obj.getValidationState() not in ('draft', 'closed') \
           and obj.getSource() == bank_account.getSource() and obj.getPath()!= bank_account.getPath():
      raise ValidationFailed("You cannot open two bank accounts for the same person on the same site")

valid_state = ["valid", "being_closed", "validating_closing",
               "being_modified", "validating_modification", "closed"]

# Check same reference do not already exists
same_ref_list = context.portal_catalog(validation_state=valid_state,
                                       portal_type="Bank Account",
                                       reference=bank_account.getReference())
for doc in same_ref_list:
  if doc.getPath() != bank_account.getPath():
    context.log("doc path %s" %(doc.getPath(),))
    raise ValidationFailed("Bank account with same reference already exists")


# Same for internal reference if exists
if bank_account.getInternalBankAccountNumber() not in ("", None):
  same_ref_list = context.portal_catalog(validation_state=valid_state,
                                         portal_type="Bank Account",
                                         string_index=bank_account.getInternalBankAccountNumber())

  for doc in same_ref_list:
    if doc.getPath() != bank_account.getPath():
      context.log("doc path %s" %(doc.getPath(),))
      raise ValidationFailed("Bank account with same internal reference already exists")
