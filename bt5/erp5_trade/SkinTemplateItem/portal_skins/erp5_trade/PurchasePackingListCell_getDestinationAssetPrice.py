line = context
delivery = line.getParentValue().getParentValue()
if delivery.getPortalType() != "Purchase Packing List":
  return None
section = delivery.getDestinationSectionValue()
source_currency = delivery.getPriceCurrencyValue()
return line.Base_getAssetPrice(
  section = section,
  source_currency = source_currency,
  delivery = delivery)
