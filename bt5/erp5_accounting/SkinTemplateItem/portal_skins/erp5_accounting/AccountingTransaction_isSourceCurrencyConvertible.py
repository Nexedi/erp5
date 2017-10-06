section_value = context.getSourceSectionValue()

if section_value is None or \
   section_value.getProperty('price_currency', None) is None:
  # If no section defined, no way to convert currencies
  return False

transaction_currency = context.getResource()
if transaction_currency is not None and\
   transaction_currency != section_value.getProperty('price_currency', None):
  return True

for line in context.getMovementList(
   portal_type=context.getPortalAccountingMovementTypeList()):
  if ((line.getSourceCredit() !=
       line.getSourceInventoriatedTotalAssetCredit()) or (
       line.getSourceDebit() !=
       line.getSourceInventoriatedTotalAssetDebit())):
    return True

return False
