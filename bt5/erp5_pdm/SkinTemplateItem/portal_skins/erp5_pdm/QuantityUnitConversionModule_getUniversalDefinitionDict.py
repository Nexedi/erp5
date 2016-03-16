def getUniversalQuantityUnitDefinitionDict():

  kw = dict(portal_type="Quantity Unit Conversion Definition",
            grand_parent_portal_type="Quantity Unit Conversion Module",
            validation_state="validated")

  result = {}
  for definition in context.portal_catalog(**kw):
    definition = definition.getObject()

    definition_group = definition.getParentValue()
    if definition_group.getValidationState() != "validated":
      continue

    standard_quantity_unit_uid = definition_group.getQuantityUnitUid()
    if standard_quantity_unit_uid is None:
      continue

    result[standard_quantity_unit_uid] = (None, 1.0)

    unit_uid = definition.getQuantityUnitUid()
    if unit_uid is None:
      continue

    definition_ratio = definition.getConversionRatio()
    if not definition_ratio:
      continue

    result[unit_uid] = (definition.getUid(), definition_ratio)

  return result

def getCategoryQuantityUnitDefinitionDict():
  quantity_unit = context.portal_categories.quantity_unit
  result = {}
  for obj in quantity_unit.getCategoryMemberValueList(portal_type="Category"):
    obj = obj.getObject()
    quantity = obj.getProperty('quantity')
    if quantity is not None:
      result[obj.getUid()] = (None, float(quantity))

  return result

def getQuantityUnitDefinitionDict():
  result = getUniversalQuantityUnitDefinitionDict()
  if not result:
    result = getCategoryQuantityUnitDefinitionDict()
  return result

from Products.ERP5Type.Cache import CachingMethod
return CachingMethod(getQuantityUnitDefinitionDict,
                     "getUniversalQuantityUnitDefinitionDict",
                     cache_factory="erp5_content_long")()
