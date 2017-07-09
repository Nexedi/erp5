from Products.PythonScripts.standard import Object
portal = context.getPortalObject()
delivery_line_data_list = []
delivery_data_list = []

checked_uid_list = portal.portal_selections.getSelectionCheckedUidsFor(module_selection_name)
if checked_uid_list:
  delivery_list = portal.portal_catalog(uid=checked_uid_list)
else:
  delivery_list = portal.portal_selections.callSelectionFor(module_selection_name, context=context)

assert mode in ('delivery', 'delivery_line')

product_type_list = portal.getPortalProductTypeList()
for delivery in delivery_list:
  delivery = delivery.getObject()
  delivery_title = delivery.getTitle()
  delivery_reference = delivery.getReference()
  delivery_description = delivery.getDescription()
  delivery_mode = delivery.getDeliveryModeTranslatedTitle()

  delivery_product_quantity_mapping = {}

  for movement in delivery.getMovementList(sort_on=[('int_index', 'ascending')]):
    # We only consider products that have to be packed
    product = movement.getResourceValue(portal_type=product_type_list) # XXX maybe `use` based ?
    if product is None:
      continue
    destination_value = movement.getDestinationValue()
    assert destination_value, "Movement %s has no destination" % movement.absolute_url()

    variation = '\n'.join([x[0] for x in movement.getVariationCategoryItemList()])
    resource_reference = movement.getResourceReference()
    resource_display_key = resource_reference
    if variation:
      resource_display_key = '%s %s' % (resource_reference, variation)
    delivery_product_quantity_mapping[resource_display_key] = (
        movement.getQuantity() +
        delivery_product_quantity_mapping.get(resource_display_key, 0))

    if mode == 'delivery_line':
      delivery_line_data_list.append(Object(
          delivery_title=delivery_title,
          delivery_reference=delivery_reference,
          delivery_mode=delivery_mode,
          source_section_title=movement.getSourceSectionTitle(),
          source_title=movement.getSourceTitle(),
          destination_section_title=movement.getDestinationSectionTitle(),
          destination_title=destination_value.getTitle(),
          destination_default_address_text=destination_value.getDefaultAddressText(),
          destination_region_title=destination_value.getRegionTranslatedTitle(),
          destination_default_telephone_coordinate_text=
              destination_value.getDefaultTelephoneCoordinateText(),
          destination_default_email_coordinate_text=
              destination_value.getDefaultEmailCoordinateText(),
          quantity=movement.getQuantity(),
          quantity_unit=movement.getQuantityUnitTranslatedTitle(),
          resource_reference=resource_reference,
          resource_title=movement.getResourceTitle(),
          variation=variation,
          start_date=movement.getStartDate(),
          stop_date=movement.getStopDate(),
          description=movement.getDescription() or delivery_description,
        ))

  if mode == 'delivery':
    destination_value = delivery.getDestinationValue()
    assert destination_value, "Delivery %s has no destination" % delivery.absolute_url()
    if set(delivery_product_quantity_mapping.values()) == set((1.,)):
      # if all quantities are 1, do not display quantities
      delivery_resource_text = '\n'.join(sorted(delivery_product_quantity_mapping.keys()))
    else:
      delivery_resource_text = '\n'.join(
        ['%s: %s' % x for x in sorted(delivery_product_quantity_mapping.items())])
    delivery_data_list.append(Object(
        delivery_title=delivery_title,
        delivery_reference=delivery_reference,
        delivery_mode=delivery_mode,
        source_section_title=delivery.getSourceSectionTitle(),
        source_title=delivery.getSourceTitle(),
        destination_section_title=delivery.getDestinationSectionTitle(),
        destination_title=destination_value.getTitle(),
        destination_default_address_text=destination_value.getDefaultAddressText(),
        destination_region_title=destination_value.getRegionTranslatedTitle(),
        destination_default_telephone_coordinate_text=
            destination_value.getDefaultTelephoneCoordinateText(),
        destination_default_email_coordinate_text=
            destination_value.getDefaultEmailCoordinateText(),
        delivery_resource_text=delivery_resource_text,
        start_date=delivery.getStartDate(),
        stop_date=delivery.getStopDate(),
        description=delivery_description,
    ))

if mode == 'delivery':
  return delivery_data_list
return delivery_line_data_list
