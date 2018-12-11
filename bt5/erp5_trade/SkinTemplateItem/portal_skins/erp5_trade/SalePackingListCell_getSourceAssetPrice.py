line = context
delivery = line.getParentValue().getParentValue()
if delivery.getPortalType() != "Sale Packing List":
  return None
section = delivery.getSourceSectionValue()
source_currency = delivery.getPriceCurrencyValue()
return line.Base_getAssetPrice(
  section = section,
  source_currency = source_currency,
  delivery = delivery)
