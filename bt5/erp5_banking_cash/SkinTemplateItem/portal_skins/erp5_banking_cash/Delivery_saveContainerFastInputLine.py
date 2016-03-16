counter_line = 0
result = []
resultContainer = {}
result_line = []

if listbox is None:
  listbox = []


def isSameSet(a, b):
  for i in a:
    if not(i in b) : return 0
  for i in b:
    if not(i in a): return 0
  if len(a) != len(b) : return 0
  return 1

# remove previous line
old_line = [x.getId() for x in context.objectValues(portal_type=[line_portal_type, container_line_portal_type])]
if len(old_line)>0:
  for line_id in old_line:
    r = context.deleteContent(line_id)

cash_container_item_dict = {}
unrestricted_catalog = context.CatalogTool_unrestrictedSearchResults

# retreive selected rows
portal = context.getPortalObject()
list_selection_name = context.REQUEST['list_selection_name']
selection_tool = context.getPortalObject().portal_selections
checked_uid_list = selection_tool.getSelectionCheckedUidsFor(list_selection_name)
context.log("Checked uid list: %s" % checked_uid_list)

for checked_uid in checked_uid_list:
    container = unrestricted_catalog(uid=checked_uid)[0].getObject()
    container_dict = {}
    container_dict["reference"] = container.getReference()
    container_dict["range_start"] = container.getCashNumberRangeStart()
    container_dict["range_stop"] = container.getCashNumberRangeStop()
    container_lines = container.objectValues(portal_type='Container Line')
    if len(container_lines) == 0:
      context.log("Delivery_saveContainerFastInputLine", "No container line find for cash container %s" %(cash_container.getRelativeUrl(),))
      continue
    container_line = container_lines[0]
    container_dict["resource"] = container_line.getResourceValue()
    container_dict["quantity"] = container_line.getQuantity()
    container_dict["variation_category"] = container_line.getVariationCategoryList()
    container_dict["base_variation_category"] = container_line.getVariationBaseCategoryList()
    cash_container_item_dict[container] = container_dict
    continue

context.log("cash_container_item_list", cash_container_item_dict)

resource_total_quantity = 0

for cash_container in cash_container_item_dict.keys():
  container_dict = cash_container_item_dict[cash_container]

  movement_container = context.newContent(portal_type          = container_line_portal_type
                                          , reindex_object     = 1
                                          , reference                 = container_dict['reference']
                                          , cash_number_range_start   = container_dict['range_start']
                                          , cash_number_range_stop    = container_dict['range_stop']
                                          )
  movement_container.setAggregateValueList([cash_container,])
  # create a cash container line
  container_line = movement_container.newContent(portal_type      = 'Container Line'
                                                 , reindex_object = 1
                                                 #, resource_value = container_dict['resource']
                                                 , quantity       = container_dict['quantity']
                                                 )

  container_line.setResourceValue(container_dict['resource'])
  container_line.setVariationCategoryList(container_dict['variation_category'])
  container_line.updateCellRange(script_id='CashDetail_asCellRange',base_id="movement")
  resource_total_quantity = 0
  for key in container_line.getCellKeyList(base_id='movement'):
    if isSameSet(key,container_dict['variation_category']):
      cell = container_line.newCell(*key)
      cell.setCategoryList(container_dict['variation_category'])
      cell.setQuantity(container_dict['quantity'])
      cell.setMappedValuePropertyList(['quantity','price'])
      cell.setMembershipCriterionBaseCategoryList(container_dict['base_variation_category'])
      cell.setMembershipCriterionCategoryList(container_dict['variation_category'])
      cell.edit(force_update = 1,
                price = container_line.getResourceValue().getBasePrice())

    resource_total_quantity += container_dict['quantity']

  movement_line = context.newContent(      portal_type    = line_portal_type,
                                           resource_value = container_dict['resource'],
                                           quantity_unit_value = context.portal_categories.quantity_unit.unit
                                           )
  movement_line.setVariationBaseCategoryList(container_dict['base_variation_category'])
  movement_line.setVariationCategoryList(container_dict['variation_category'])
  movement_line.updateCellRange(script_id="CashDetail_asCellRange", base_id="movement")
  for key in movement_line.getCellKeyList(base_id='movement'):
    if isSameSet(key,container_dict['variation_category']):
      cell = movement_line.newCell(*key)
      cell.setCategoryList(container_dict['variation_category'])
      cell.setQuantity(resource_total_quantity)
      cell.setMappedValuePropertyList(['quantity','price'])
      cell.setMembershipCriterionBaseCategoryList(container_dict['base_variation_category'])
      cell.setMembershipCriterionCategoryList(container_dict['variation_category'])
      cell.edit(force_update = 1,
                  price = movement_line.getResourceValue().getBasePrice())
  # Call getPrice so lines are modified before being stored, not on indexation. Sigh.
  container_line.getPrice()

request  = context.REQUEST
redirect_url = '%s/view?%s' % ( context.absolute_url()
                                , 'portal_status_message=done'
                                )
request[ 'RESPONSE' ].redirect( redirect_url )
