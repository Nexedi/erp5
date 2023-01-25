from Products.ERP5Type.Message import translateString

source = context.Item_getCurrentSiteValue()
source_section = context.Item_getCurrentOwnerValue()

module = context.getDefaultModule(portal_type=portal_type)
line_portal_type = '%s Line' % portal_type
cell_portal_type = '%s Cell' % portal_type

delivery = module.newContent(title=title,
                             source_value=source,
                             source_section_value=source_section,
                             portal_type=portal_type)

delivery_line = delivery.newContent(
                    portal_type=line_portal_type,
                    title=context.getReference(),
                    quantity_unit=context.getQuantityUnit(),
                    resource_value=context.Item_getResourceValue())

variation_category_list = context.Item_getVariationCategoryList()

if not variation_category_list:
  delivery_line.edit(
              price=context.getPrice(),
              quantity=context.getQuantity(),
              aggregate_value=context)
else:
  delivery_line.setVariationCategoryList(variation_category_list)
  base_id = 'movement'
  cell_key_list = list(delivery_line.getCellKeyList(base_id=base_id))
  cell_key_list.sort()
  for cell_key in cell_key_list:
    cell = delivery_line.newCell(base_id=base_id,
                                 portal_type=cell_portal_type,
                                 *cell_key)
    cell.edit(mapped_value_property_list=['price','quantity'],
              price=context.getPrice(),
              quantity=context.getQuantity(),
              predicate_category_list=cell_key,
              variation_category_list=cell_key,
              aggregate_value=context)

return delivery.Base_redirect('view', keep_items=dict(
                                 portal_status_message=translateString('Item affected')))
