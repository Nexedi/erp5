# This script indexes the preferred Transformation to produce
# a variation of a product.
# transformation_item_list is a list of:
#   transformation, variation_list_list
# transformation is a transformation to index, while variation_list_list
# is a list of variation categories that are relevant for the produced resource



# List of dictionaries:
#   { id:resource_id,
#     variation_text: resource_variation_text,
#     row_dict_list: list of rows to insert; each row is represented as a dict.}
row_dict_dict_list = []

portal = context.getPortalObject()
for transformation_relative_url, variation_list_list in transformation_item_list:
  transformation = portal.restrictedTraverse(transformation_relative_url)
  resource = transformation.getResourceValue()

  if resource is None:
    continue
  for variation_list in variation_list_list:
    movement = resource.newContent(temp_object=True, portal_type='Movement',
                               id='temp',
                               specialise_value=transformation,
                               variation_category_list=variation_list,
                               resource_value=resource,
                               quantity=1.0)
    base_row = dict(uid=resource.getUid(), variation_text=movement.getVariationText())

    row_dict_list = []
    for amount in movement.getAggregatedAmountList():
      transformed_resource_uid = amount.getResourceUid()
      quantity = amount.getQuantity()
      if transformed_resource_uid is not None and quantity is not None:
        row_dict = base_row.copy()
        row_dict.update(transformed_uid=transformed_resource_uid,
                        transformed_variation_text=amount.getVariationText(),
                        quantity=quantity)
        row_dict_list.append(row_dict)

    base_row['row_dict_list'] = row_dict_list
    row_dict_dict_list.append(base_row)

context.z_catalog_transformation_list(row_dict_dict_list=row_dict_dict_list)
