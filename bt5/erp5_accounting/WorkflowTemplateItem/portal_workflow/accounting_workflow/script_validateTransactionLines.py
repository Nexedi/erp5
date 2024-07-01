"""Validate Transaction Lines for source and destination section.

XXX why proxy role ???
"""

from Products.ERP5Type.Core.Workflow import ValidationFailed
from Products.ERP5Type.Message import translateString

transaction = state_change['object']
portal = transaction.getPortalObject()
bank_account_portal_type = portal.getPortalPaymentNodeTypeList()
section_portal_type_list = ['Person', 'Organisation']
invalid_state_list = ['invalidated', 'deleted']

# first of all, validate the transaction itself
container.script_validateTransaction(state_change)


# Check that all lines uses open accounts, and doesn't use invalid third
# parties or bank accounts
transaction_lines = transaction.objectValues(portal_type=transaction.getPortalAccountingMovementTypeList())
id_to_delete_list = []
getBankAccountItemList = portal.AccountModule_getBankAccountItemList
for line in transaction_lines:
  for account, third_party, bank_account, bank_account_relative_url_list_getter in (
    (
      line.getSourceValue(portal_type='Account'),
      line.getDestinationSectionValue(portal_type=section_portal_type_list),
      line.getSourcePaymentValue(portal_type=bank_account_portal_type),
      lambda: (x[1] for x in getBankAccountItemList(
        organisation=line.getSourceSection(portal_type=section_portal_type_list))),    # pylint:disable=cell-var-from-loop
    ),
    (
      line.getDestinationValue(portal_type='Account'),
      line.getSourceSectionValue(portal_type=section_portal_type_list),
      line.getDestinationPaymentValue(portal_type=bank_account_portal_type),
      lambda: (x[1] for x in getBankAccountItemList(
        organisation=line.getDestinationSection(portal_type=section_portal_type_list))),    # pylint:disable=cell-var-from-loop
    ),
  ):
    if account is not None and account.getValidationState() != 'validated':
      raise ValidationFailed(translateString(
          "Account ${account_title} is not validated.",
           mapping=dict(account_title=account.Account_getFormattedTitle())))

    if third_party is not None and\
        third_party.getValidationState() in invalid_state_list:
      raise ValidationFailed(translateString(
          "Third party ${third_party_name} is invalid.",
           mapping=dict(third_party_name=third_party.getTitle())))

    if bank_account is not None:
      if bank_account.getRelativeUrl() not in bank_account_relative_url_list_getter():
        raise ValidationFailed(translateString(
            "Bank Account ${bank_account_reference} is invalid.",
             mapping=dict(bank_account_reference=bank_account.getReference())))

      if account is not None and account.isMemberOf('account_type/asset/cash/bank'):
        # also check that currencies are consistent if we use this quantity for
        # accounting.
        bank_account_currency = bank_account.getProperty('price_currency')
        if bank_account_currency is not None and \
              bank_account_currency != line.getResource():
          raise ValidationFailed(translateString(
            "Bank Account ${bank_account_reference} "
            "uses ${bank_account_currency} as default currency.",
            mapping=dict(bank_account_reference=bank_account.getReference(),
                         bank_account_currency=bank_account.getPriceCurrencyReference())))

  source_currency = None
  source_section = line.getSourceSectionValue()
  if source_section is not None:
    source_currency = source_section.getProperty('price_currency')

  if source_currency == line.getResource():
    if ((line.getSourceCredit() !=
         line.getSourceInventoriatedTotalAssetCredit()) or (
         line.getSourceDebit() !=
         line.getSourceInventoriatedTotalAssetDebit())):
      raise ValidationFailed(translateString(
              "Source conversion should not be set."))

  destination_currency = None
  destination_section = line.getDestinationSectionValue()
  if destination_section is not None:
    destination_currency = destination_section.getProperty('price_currency')

  if destination_currency == line.getResource():
    if ((line.getDestinationCredit() !=
         line.getDestinationInventoriatedTotalAssetCredit()) or (
         line.getDestinationDebit() !=
         line.getDestinationInventoriatedTotalAssetDebit())):
      raise ValidationFailed(translateString(
              "Destination conversion should not be set."))

  if line.getSourceInventoriatedTotalAssetPrice() or \
     line.getDestinationInventoriatedTotalAssetPrice() or \
     line.isSimulated():
    continue
  id_to_delete_list.append(line.getId())

# Delete empty lines
# Don't delete everything
if len(id_to_delete_list) != len(transaction_lines):
  transaction.deleteContent(id_to_delete_list)
