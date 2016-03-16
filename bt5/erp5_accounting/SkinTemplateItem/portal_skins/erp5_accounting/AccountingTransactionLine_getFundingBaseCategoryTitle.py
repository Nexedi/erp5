portal = context.getPortalObject()

funding_base_category = portal.portal_preferences.getPreferredAccountingTransactionLineFundingBaseCategory()

if funding_base_category:
  return portal.portal_categories.restrictedTraverse(funding_base_category).getBaseCategoryValue().getTitle()

return 'Funding'
