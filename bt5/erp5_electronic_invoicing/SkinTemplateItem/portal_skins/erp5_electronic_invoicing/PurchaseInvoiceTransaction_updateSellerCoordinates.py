aggregate_value = context.getAggregateValue()
if aggregate_value is None:
  return
connector_value = aggregate_value.getSourceValue()
aggregate_property_dict = connector_value.SuperPDPInvoicingConnector_getInvoiceSellerPropertyList(aggregate_value.getTextContent())

source_section_value = context.getSourceSectionValue()
if source_section_value is None:
  return
edit_dict = { k: v for (k, v) in aggregate_property_dict.items() if k not in source_section_value }
if len(edit_dict) > 0:
  source_section_value.edit(**edit_dict)
