# This script create inventory for a bunch of node uid
from DateTime import DateTime
date = DateTime(inventory_date)
node_inventory_list = []
payment_inventory_list = []
if len(node_uid_list):
  node_inventory_list = context.portal_simulation.getCurrentInventoryList(node_uid=node_uid_list,
                                                                     at_date=inventory_date,
                                                                     group_by_variation=1,
                                                                     group_by_resource=1,
                                                                     group_by_section=1,
                                                                     group_by_node=1,
                                                                     connection_id=source_connection_id)

if len(payment_uid_list):
  payment_inventory_list = context.portal_simulation.getCurrentInventoryList(payment_uid=payment_uid_list,
                                                                     at_date=inventory_date,
                                                                     group_by_variation=1,
                                                                     group_by_resource=1,
                                                                     group_by_section=1,
                                                                     group_by_payment=1,
                                                                     connection_id=source_connection_id)

inventory_module = context.getPortalObject().archive_inventory_module
node_inventory_dict = {}
activate_kw = {"tag": tag}
for inventory in node_inventory_list:
  # Do only one inventory per node
  if inventory.node_relative_url not in node_inventory_dict:

    inv = inventory_module.newContent(portal_type="Archive Inventory",
                                      destination=inventory.node_relative_url,
                                      start_date = date,
                                      activate_kw = activate_kw,
                                      reindex_kw = {"sql_catalog_id" : destination_sql_catalog_id})
    node_inventory_dict[inventory.node_relative_url] = inv
  else:
    inv = node_inventory_dict[inventory.node_relative_url]

  inv.setDefaultActivateParameterDict(activate_kw)
  inv.setDefaultReindexParameterDict(dict(sql_catalog_id=destination_sql_catalog_id))
  # Create one line per resource
  inv_line = inv.newContent(portal_type = "Archive Inventory Line",
                            resource=inventory.resource_relative_url,
                            destination_section=inventory.section_relative_url,
                            activate_kw = activate_kw,
                            reindex_kw = {"sql_catalog_id" : destination_sql_catalog_id})
  inv_line.setDefaultActivateParameterDict(activate_kw)
  inv_line.setDefaultReindexParameterDict(dict(sql_catalog_id=destination_sql_catalog_id))
  # This is a hack so that price is now and not at reindexing part
  inv_line.getPrice()

  if inventory.variation_text in ("", None):
    inv_line.edit(quantity=inventory.total_quantity)
  else:
    # construct base category list
    variation_category_list = inventory.variation_text.split('\n')
    base_category_list = []
    for variation in variation_category_list:
      base_category_list.append(variation.split("/")[0])

    # set base category list on line
    inv_line.setVariationBaseCategoryList(base_category_list)
    # set category list line
    inv_line.setVariationCategoryList(variation_category_list)
    context.log("construct cell", "base %s, %s" %(base_category_list,variation_category_list))
    base_id = "movement"
    line_kwd = {'base_id':base_id, "activate_kw": activate_kw}
    inv_line.updateCellRange(script_id='CashDetail_asCellRange', base_id=base_id)
    # create cell
    cell_range_key_list = inv_line.getCellRangeKeyList(base_id=base_id)
    if cell_range_key_list != [[None, None]] :
      for k in cell_range_key_list:
        category_list = filter(lambda k_item: k_item is not None, k)
        cell = inv_line.newCell(*k, **line_kwd)
        cell.setDefaultActivateParameterDict(activate_kw)
        cell.setDefaultReindexParameterDict(dict(sql_catalog_id=destination_sql_catalog_id))

        mapped_value_list = ['price', 'quantity']
        cell.edit( membership_criterion_category_list = category_list
                   , mapped_value_property_list         = mapped_value_list
                   , category_list                      = category_list
                   , force_update                       = 1
                   )
        cell.setQuantity(inventory.total_quantity)



# deliver all inventory
for inv in node_inventory_dict.values():
  inv.setDefaultActivateParameterDict(activate_kw)
  inv.setDefaultReindexParameterDict(dict(sql_catalog_id=destination_sql_catalog_id))
  inv.deliver()




# same for payment uid
payment_inventory_dict = {}
for inventory in payment_inventory_list:
  # Do only one inventory per payment
  if inventory.payment_uid not in payment_inventory_dict:

    inv = inventory_module.newContent(portal_type="Archive Inventory",
                                      destination=inventory.node_relative_url,
                                      destination_payment_uid=inventory.payment_uid,
                                      start_date = date,
                                      activate_kw = activate_kw,
                                      reindex_kw = {"sql_catalog_id" : destination_sql_catalog_id})
    payment_inventory_dict[inventory.payment_uid] = inv
  else:
    inv = payment_inventory_dict[inventory.payment_uid]

  inv.setDefaultActivateParameterDict(activate_kw)
  inv.setDefaultReindexParameterDict(dict(sql_catalog_id=destination_sql_catalog_id))
  # Create one line per resource
  inv_line = inv.newContent(portal_type = "Archive Inventory Line",
                            resource=inventory.resource_relative_url,
                            destination_section=inventory.section_relative_url,
                            activate_kw = activate_kw,
                            reindex_kw = {"sql_catalog_id" : destination_sql_catalog_id})
  inv_line.setDefaultActivateParameterDict(activate_kw)
  inv_line.setDefaultReindexParameterDict(dict(sql_catalog_id=destination_sql_catalog_id))
  inv_line.edit(quantity=inventory.total_quantity)
  # This is a hack so that price is now and not at reindexing part
  inv_line.getPrice()


# deliver all inventory
for inv in payment_inventory_dict.values():
  inv.setDefaultActivateParameterDict(activate_kw)
  inv.setDefaultReindexParameterDict(dict(sql_catalog_id=destination_sql_catalog_id))
  inv.deliver()
