if context.getResource() and context.getResourceValue().getAggregatedPortalTypeList()\
   and context.isMovement()\
   and (('Cell' in context.getPortalType()) or not context.getVariationCategoryList()):
  return True
