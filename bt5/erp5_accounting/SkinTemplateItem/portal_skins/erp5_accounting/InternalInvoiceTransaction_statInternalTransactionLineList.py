from Products.PythonScripts.standard import Object
total_source_debit = 0
total_source_credit = 0
total_destination_debit = 0
total_destination_credit = 0
total_source_asset_debit = 0
total_source_asset_credit = 0
total_destination_asset_debit = 0
total_destination_asset_credit = 0

currency_precision = context.getQuantityPrecisionFromResource(context.getResource())
source_section_precision = 2
source_section = context.getSourceSectionValue(portal_type='Organisation')
if source_section is not None:
  source_section_precision = context.getQuantityPrecisionFromResource(source_section.getPriceCurrency())
destination_section_precision = 2
destination_section = context.getDestinationSectionValue(portal_type='Organisation')
if destination_section is not None:
  destination_section_precision = context.getQuantityPrecisionFromResource(destination_section.getPriceCurrency())

source_section = context.getSourceSection()
destination_section = context.getDestinationSection()
for line in context.objectValues(
        portal_type = context.getPortalAccountingMovementTypeList()) :
  if line.getSource() and line.getSourceSection() == source_section:
    total_source_debit += round(line.getSourceDebit(), currency_precision)
    total_source_asset_debit += round(line.getSourceInventoriatedTotalAssetDebit(), source_section_precision)
    total_source_credit += round(line.getSourceCredit(), currency_precision)
    total_source_asset_credit += round(line.getSourceInventoriatedTotalAssetCredit(), source_section_precision)
  if line.getDestination()\
      and line.getDestinationSection() == destination_section:
    total_destination_debit += round(line.getDestinationDebit(), currency_precision)
    total_destination_asset_debit += round(line.getDestinationInventoriatedTotalAssetDebit(), destination_section_precision)
    total_destination_credit += round(line.getDestinationCredit(), currency_precision)
    total_destination_asset_credit += round(line.getDestinationInventoriatedTotalAssetCredit(), destination_section_precision)

return [Object(
          source_debit=total_source_debit,
          source_credit=total_source_credit,
          destination_debit=total_destination_debit,
          destination_credit=total_destination_credit,
          source_asset_debit=total_source_asset_debit,
          source_asset_credit=total_source_asset_credit,
          destination_asset_debit=total_destination_asset_debit,
          destination_asset_credit=total_destination_asset_credit,)]
