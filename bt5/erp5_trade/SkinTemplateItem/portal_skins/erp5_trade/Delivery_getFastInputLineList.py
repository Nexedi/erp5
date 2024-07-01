"""
  This script creates a list of empty lines when called with
  read_document_lines to False. Otherwise, it displays on
  the fast input all documents lines already added
"""
request = context.REQUEST
portal = context.getPortalObject()
trade_document = context
result = []
# Retrieve lines portal type
line_portal_type_list = [x for x in context.getTypeInfo().getTypeAllowedContentTypeList() \
                         if x in portal.getPortalMovementTypeList()]
line_portal_type = line_portal_type_list[0]

if read_document_lines:
  line_list = context.contentValues(portal_type=line_portal_type)
else:
  line_list = []

if line_portal_type in portal.getPortalSaleTypeList():
  section_uid = context.getSourceSectionUid()
elif line_portal_type in portal.getPortalPurchaseTypeList():
  section_uid = context.getDestinationSectionUid()
else:
  section_uid = None
len_line_list = len(line_list)
used_id = [] # list use to make sure we do not generate two line with same id/uid
used_id_append = used_id.append
result_append = result.append

# first browse document's lines
for line in line_list:
  resource = line.getResourceValue()

  line_id = int(line.getId())

  # First check if cells are defined
  cell_list = line.getCellValueList()
  if len(cell_list):
    for cell in cell_list:
      while line_id in used_id:
        # do not used an id from previously generated lines
        line_id+=1
      #context.log("inventory values a = %s, c = %s, f = %s" %(resource.getAvailableInventory(
      #  section_uid=section_uid,
      #  variation_text=cell.getVariationText()),
      #                                                        resource.getCurrentInventory(
      #  section_uid=section_uid,
      #  variation_text=cell.getVariationText()),
      #                                                        resource.getInventory(
      #  section_uid=section_uid,
      #  variation_text=cell.getVariationText())))

      obj = trade_document.newContent(portal_type=line_portal_type,
                                      id=line_id,
                                      source=cell.getRelativeUrl(), # use as a link to the already create line/cell
                                      uid="new_%s" % line_id,
                                      temp_object=1,
                                      is_indexable=0,
                                      title=resource.getTitle(),
                                      resource_value=resource,
                                      reference=resource.getReference(),
                                      quantity=cell.getQuantity(),
                                      price=cell.getPrice(),
                                      total_price=cell.getTotalPrice(),
                                      variation_category_list = cell.getVariationCategoryList(),
                                      available_quantity=resource.getAvailableInventory(
                                                                 section_uid=section_uid,
                                                                 variation_text=cell.getVariationText()),
                                      current_quantity=resource.getCurrentInventory(
                                                                 section_uid=section_uid,
                                                                 variation_text=cell.getVariationText()),
                                      inventory=resource.getInventory(
                                                                 section_uid=section_uid,
                                                                 variation_text=cell.getVariationText()))
      result_append(obj)
      used_id_append(line_id)
  else:
    while line_id in used_id:
      # do not used an id from previously generated lines
      line_id+=1
    #context.log("inventory values a = %s, c = %s, f = %s" %(resource.getAvailableInventory(
    #    section_uid=section_uid,
    #    variation_text=line.getVariationText()),
    #                                                          resource.getCurrentInventory(
    #    section_uid=section_uid,
    #    variation_text=line.getVariationText()),
    #                                                          resource.getInventory(
    #    section_uid=section_uid,
    #    variation_text=line.getVariationText())))

    obj = trade_document.newContent(portal_type=line_portal_type,
                                    id=line_id,
                                    uid="new_%s" % line_id,
                                    source=line.getRelativeUrl(),
                                    temp_object=1,
                                    is_indexable=0,
                                    title=resource.getTitle(),
                                    resource_value=resource,
                                    reference=resource.getReference(),
                                    quantity=line.getQuantity(),
                                    price = line.getPrice(),
                                    total_price=line.getTotalPrice(),
                                    variation_category_list = line.getVariationCategoryList(),
                                    available_quantity=resource.getAvailableInventory(
                                                               section_uid=section_uid,
                                                               variation_text=line.getVariationText()),
                                    current_quantity=resource.getCurrentInventory(
                                                               section_uid=section_uid,
                                                               variation_text=line.getVariationText()),
                                    inventory=resource.getInventory(
                                                               section_uid=section_uid,
                                                               variation_text=line.getVariationText()))

    result_append(obj)
    used_id_append(line_id)

# then add empty lines
empty_line_cpt = 1 # this counter is used so that we always add a fix
                   # number of empty lines into the listbox, thus user
                   # just have to click "update" to get new empty lines
i = len_line_list + 1
if read_document_lines is False:
  while empty_line_cpt <= lines_num:
    while i in used_id:
      # do not used an id from previously generated lines
      i+=1
    # Retrieve values set by the update script
    resource_relative_url = getattr(request,"field_listbox_resource_relative_url_new_%s"%i,None)
    resource_title = getattr(request,"field_listbox_title_new_%s"%i,None)
    reference = getattr(request,"field_listbox_reference_new_%s"%i,None)

    obj=trade_document.newContent(portal_type=line_portal_type,
                                   id = i,
                                   uid="new_%s" % i,
                                   temp_object=1,
                                   reference=None, # otherwise it is acquired on parent
                                   is_indexable=0,)

    used_id_append(i)
    # Set values inputted by user
    if resource_title not in ('',None):
      empty_line_cpt -= 1
      obj.edit(resource_title=resource_title)
    if reference not in ('',None):
      empty_line_cpt -= 1
      obj.edit(reference=reference)
     # if a resource is selected, use it
    if resource_relative_url not in ('',None):
      empty_line_cpt -= 1
      resource = portal.restrictedTraverse(resource_relative_url)
      obj.setResourceValue(resource)
    empty_line_cpt += 1
    result_append(obj)

return result
