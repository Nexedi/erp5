portal = context.getPortalObject()

function_base_category = portal.portal_preferences.getPreferredAccountingTransactionLineFunctionBaseCategory()

if function_base_category:
  return portal.portal_categories.restrictedTraverse(function_base_category).getBaseCategoryValue().getTitle()

return 'Function'
