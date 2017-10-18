production_order_line = context
portal = production_order_line.getPortalObject()

transformation = production_order_line.getSpecialiseValue(
  portal_type=portal.getPortalTransformationTypeList())
if transformation is None \
    or (transformation.getResource() != production_order_line.getResource()):
  resource_uid = production_order_line.getResourceUid()
  if resource_uid:
    transformation_list = portal.portal_catalog(
      portal_type=portal.getPortalTransformationTypeList(),
      validation_state="!=invalidated",
      default_resource_uid=resource_uid)
    if len(transformation_list) == 1:
      transformation = transformation_list[0].getRelativeUrl()
      production_order_line.setSpecialise(transformation)
      return
  production_order_line.setSpecialise(None)
