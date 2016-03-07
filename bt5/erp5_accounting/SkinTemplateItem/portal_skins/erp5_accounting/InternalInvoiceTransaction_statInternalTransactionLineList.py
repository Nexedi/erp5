from Products.PythonScripts.standard import Object
total_source_debit = 0
total_source_credit = 0
total_destination_debit = 0
total_destination_credit = 0
total_source_asset_debit = 0
total_source_asset_credit = 0
total_destination_asset_debit = 0
total_destination_asset_credit = 0

source_section = context.getSourceSection()
destination_section = context.getDestinationSection()
for line in context.objectValues(
        portal_type = context.getPortalAccountingMovementTypeList()) :
  if line.getSource() and line.getSourceSection() == source_section:
    total_source_debit += line.getSourceDebit()
    total_source_asset_debit += line.getSourceInventoriatedTotalAssetDebit()
    total_source_credit += line.getSourceCredit()
    total_source_asset_credit += line.getSourceInventoriatedTotalAssetCredit()
  if line.getDestination()\
      and line.getDestinationSection() == destination_section:
    total_destination_debit += line.getDestinationDebit()
    total_destination_asset_debit += line.getDestinationInventoriatedTotalAssetDebit()
    total_destination_credit += line.getDestinationCredit()
    total_destination_asset_credit += line.getDestinationInventoriatedTotalAssetCredit()

return [Object(
          source_debit=total_source_debit,
          source_credit=total_source_credit,
          destination_debit=total_destination_debit,
          destination_credit=total_destination_credit,
          source_asset_debit=total_source_asset_debit,
          source_asset_credit=total_source_asset_credit,
          destination_asset_debit=total_destination_asset_debit,
          destination_asset_credit=total_destination_asset_credit,)]
