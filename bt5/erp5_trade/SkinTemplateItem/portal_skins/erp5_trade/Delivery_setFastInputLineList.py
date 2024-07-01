"""
  This script creates or updates trade document lines based on the fast
  input information.It should take into account any trade document line
  which were already created so that they are not duplicated.
"""
# pylint:disable=possibly-used-before-assignment

from Products.ERP5Type.Message import translateString
portal = context.getPortalObject()

# Retrieve line and cell portal type
line_portal_type_list = [x for x in context.getTypeInfo().getTypeAllowedContentTypeList() \
                         if x in portal.getPortalMovementTypeList()]
line_portal_type = line_portal_type_list[0]
cell_portal_type_list = [x for x in portal.portal_types[line_portal_type].getTypeAllowedContentTypeList() \
                         if x in portal.getPortalMovementTypeList()]
cell_portal_type = cell_portal_type_list[0]

per_resource_line_dict = {}

for line in listbox:
  # Only create line if user has selected a resource
  if 'listbox_key' in line and (line.get('resource_relative_url', None) not in ("", None) \
                                      or line.get('source', None) not in ("", None)):

    if line.get('resource_relative_url', None) not in ("", None):
      product = portal.restrictedTraverse(line["resource_relative_url"])

    if line.get('source', None) not in ("", None):
      source_document = portal.restrictedTraverse(line['source'])
      product = source_document.getResourceValue()
    else:
      source_document = None

    # update original line/cell if given
    if source_document is not None:
      edit_kw = {}
      if 'quantity' in line:
        # if quantity is editable field
        edit_kw['quantity'] = line['quantity']
      if 'price' in line:
        # if price is editable field
        edit_kw['price'] = line['price']
      source_document.edit(**edit_kw)
    else:
      # if there was no document line already defined
      # for the document, add a new document line

      # We check if haven't already create a line for the same resource
      key = "%s" %(product.getRelativeUrl(),)
      trade_document_line = per_resource_line_dict.get(key, None)
      if trade_document_line is None:
        trade_document_line= context.newContent(portal_type=line_portal_type,
                                                resource_value=product,
                                                reference=product.getReference(),
                                                title=product.getTitle(),
                                                )
      per_resource_line_dict[key] = trade_document_line
      variation_category_list = line["variation_category_list"]
      if variation_category_list:
        variation_category_list.sort()
        trade_document_line.setVariationCategoryList(trade_document_line.getVariationCategoryList()+variation_category_list)
        base_id = 'movement'
        cell_key_list = list(trade_document_line.getCellKeyList(base_id=base_id))
        for cell_key in cell_key_list:
          sorted_cell_key = cell_key[:]
          sorted_cell_key.sort()
          if sorted_cell_key == variation_category_list:
            cell = trade_document_line.newCell(base_id=base_id,
                                               portal_type=cell_portal_type, *cell_key)
            cell.edit(mapped_value_property_list=['price','quantity'],
                      price=line['price'], quantity=line['quantity'],
                      quantity_unit = line["quantity_unit"],
                      predicate_category_list=cell_key,)
            cell.setVariationCategoryList(cell_key)
      else:
        trade_document_line.edit(quantity = line["quantity"],
                                 price = line["price"],
                                 quantity_unit=line['quantity_unit']
                                 )

return context.Base_redirect(kw['form_id'], keep_items=dict(
        portal_status_message=translateString('%s Created.' %(line_portal_type,))))
