"""
  Add a data supply structure for a data ingestion on a portal ingestion policy.
"""
data_supply = context.data_supply_module.newContent( \
                portal_type='Data Supply', **data_supply_kw)
data_supply.validate()

# add default line
data_supply_line = data_supply.newContent(portal_type='Data Supply Line', \
                                          **data_supply_line_kw)

return data_supply
