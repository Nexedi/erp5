"""
This script returns only the quantity unit of the resource
entered on the fast input
"""
request = context.REQUEST
portal = context.getPortalObject()

result_item_list = [('', '')]

resource_value = context.getResourceValue()
if resource_value is None:
  # Lookup for expected resource according parameters in REQUEST
  resource_relative_url = request.form.get("field_listbox_resource_relative_url_%s" % context.getUid())
  if resource_relative_url:
    resource_value = portal.restrictedTraverse(resource_relative_url)
  resource_title = request.form.get("field_listbox_title_%s" % context.getUid())
  resource_reference = request.form.get("field_listbox_reference_%s" % context.getUid())
  if resource_value is None and (resource_title or resource_reference):
    # Querying catalog to find a resource according title and reference parameters
    # like Delivery_updateFastInputLineList does.
    delivery = context
    if delivery.getPortalType() in portal.getPortalContainerLineTypeList():
      delivery = context.getExplanationValue()
    line_portal_type_list = [x for x in delivery.getTypeInfo().getTypeAllowedContentTypeList() \
                             if x in portal.getPortalMovementTypeList()]
    line_portal_type = line_portal_type_list[0]

    if line_portal_type in portal.getPortalSaleTypeList():
      use_list = portal.portal_preferences.getPreferredSaleUseList()
    elif line_portal_type in portal.getPortalPurchaseTypeList():
      use_list = portal.portal_preferences.getPreferredPurchaseUseList()
    elif line_portal_type in portal.getPortalInternalTypeList():
      use_list = portal.portal_preferences.getPreferredPurchaseUseList() \
               + portal.portal_preferences.getPreferredSaleUseList()
    elif line_portal_type in portal.getPortalInventoryMovementTypeList():
      use_list = portal.portal_preferences.getPreferredPurchaseUseList() \
                 + portal.portal_preferences.getPreferredSaleUseList()
    else:
      raise NotImplementedError('Line portal type not found %s' % (line_portal_type,))
    use_uid_list = [portal.portal_categories.getCategoryUid(use) for use in use_list]
    resource_list = portal.portal_catalog(portal_type=portal.getPortalResourceTypeList(),
                                          title=resource_title,
                                          default_use_uid=use_uid_list,
                                          reference=resource_reference)
    if len(resource_list):
      resource_value = resource_list[0]

if resource_value is not None:
  quantity_unit_list = [(x.getTranslatedLogicalPath(), x.getCategoryRelativeUrl(base=0))
                       for x in resource_value.getQuantityUnitValueList()]
  # return the first quantity_unit item of resource
  result_item_list.extend(quantity_unit_list)

return result_item_list
