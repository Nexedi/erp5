"""
  Create all required types for proper ingestion into Wendelin.
"""
from DateTime import DateTime

now = DateTime()
ingestion_policy = context.newContent( \
      id = reference,
      title = title,
      portal_type ='Ingestion Policy',
      reference = reference,
      version = '001',
      script_id = 'IngestionPolicy_parseSimpleFluentdTag')
ingestion_policy.validate()


use_category = context.restrictedTraverse("portal_categories/use/big_data/ingestion")
quantity_category = context.restrictedTraverse("portal_categories/quantity_unit/unit/piece")
data_operation = context.restrictedTraverse("data_operation_module/wendelin_1")

# create Data Product
data_product = context.data_product_module.newContent(
                 portal_type = "Data Product",
                 title = "Append to Data Stream",
                 reference = reference)
data_product.setUseValue(use_category)
data_product.setAggregatedPortalTypeList(["Data Stream"])
data_product.validate()

# create Data Supply
data_supply_kw = {'title': title,
                  'reference': reference,
                  'version': '001',
                  'effective_date': now,
                  'expiration_date': now + 365*10}
data_supply = context.data_supply_module.newContent( \
                portal_type='Data Supply', **data_supply_kw)
data_supply.validate()

# add ingestion line
data_supply_line_kw = {'title': 'Ingest Data',
                       'reference': 'ingestion_operation',
                       'int_index': 1,
                       'quantity': 1.0}
data_supply_line = data_supply.newContent(portal_type='Data Supply Line', \
                                          **data_supply_line_kw)
data_supply_line.setResourceValue(data_operation)

# add append to Data Stream line
data_supply_line_kw = {'title': 'Data Stream',
                       'reference': 'out_stream',
                       'int_index': 2,
                       'quantity': 1.0}
data_supply_line = data_supply.newContent(portal_type='Data Supply Line', \
                                          **data_supply_line_kw)
data_supply_line.setResourceValue(data_product)
data_supply_line.setUseValue(use_category) 

if batch_mode:
  return ingestion_policy, data_supply, data_product
else:
  # UI case
  ingestion_policy.Base_redirect(\
                    form_id='view', \
                    keep_items={'portal_status_message': \
                      context.Base_translateString('Ingestion Policy added.')})
