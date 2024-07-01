# Creates one Order/Packing list per Different Source sections
# Creates one Line per Resource
from Products.ERP5Type.Message import translateString
selection_name = "item_module_selection"
cell_portal_type = '%s Cell' % portal_type
portal = context.getPortalObject()
stool = portal.portal_selections
getObject = portal.portal_catalog.getObject


selection_uid_list = stool.getSelectionCheckedUidsFor(selection_name)

if selection_uid_list:
  object_list = [getObject(uid) for uid in selection_uid_list]
else:
  object_list = stool.callSelectionFor(selection_name)

source_section_list = [  item.Item_getCurrentOwnerValue() for item in object_list ]

property_dict = {'title':title,
                 'portal_type' : portal_type, }

module = context.getDefaultModule(portal_type=portal_type)
line_portal_type = '%s Line' % portal_type

pl_property_dict = {}
for k,v in property_dict.items():
  pl_property_dict[k]=v

pl_dict = {}

for ss in source_section_list:
  if ss is not None:
    uid = str(ss.getUid())
  else:
    uid = 'UID'

  if uid not in pl_dict:
    pl_dict[uid] = module.newContent(**pl_property_dict)
    pl_dict[uid].setSourceSectionValue(ss)

delivery_count = len(source_section_list)

for item in object_list:
  source_section = item.Item_getCurrentOwnerValue()
  if source_section is not None:
    pl_value = pl_dict[str(source_section.getUid())]
  else:
    pl_value = pl_dict['UID']

  source = item.Item_getCurrentSiteValue()
  resource = item.Item_getResourceValue()

  pl_line_dict = {}
  pl_line_dict['portal_type'] = line_portal_type

  pl_line_dict['title']= item.getReference()
  pl_line_dict['quantity'] = item.getQuantity()
  pl_line_dict['quantity_unit'] = item.getQuantityUnit()
  pl_line_dict['resource_value'] = resource
  pl_line_dict['source_value'] = source
  pl_line_value = pl_value.newContent(**pl_line_dict)
  variation_category_list = item.Item_getVariationCategoryList()
  if not variation_category_list:
    pl_line_value.setAggregateValue(item)
  else:
    pl_line_value.setVariationCategoryList(variation_category_list)
    base_id = 'movement'
    cell_key_list = list(pl_line_value.getCellKeyList(base_id=base_id))
    cell_key_list.sort()
    for cell_key in cell_key_list:
      cell = pl_line_value.newCell(base_id=base_id, \
                                portal_type=cell_portal_type,*cell_key)
      cell.edit(mapped_value_property_list=['price','quantity'],
                price=item.getPrice(), quantity=item.getQuantity(),
                predicate_category_list=cell_key,
                variation_category_list=cell_key)
      cell.setAggregateValue(item)

if delivery_count == 1:
  return pl_value.Base_redirect('view', keep_items=dict(
       portal_status_message=translateString(
         'Items affected')))

return context.Base_redirect(form_id, keep_items=dict(
       portal_status_message=translateString(
         'Items affected in ${delivery_count} deliveries.',
         mapping=dict(delivery_count=delivery_count))))
