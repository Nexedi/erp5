search_kw = {}
portal = context.getPortalObject()
financial_section_list = context.getVariationCategoryList(base_category_list=('financial_section'))
for financial_section in financial_section_list:
  search_kw.setdefault('financial_section_uid', []).append(
    portal.portal_categories.restrictedTraverse(financial_section).getUid())

account_list = [a.getObject() for a in portal.account_module.searchFolder(
               validation_state='validated', **search_kw)]

account_list.sort(key=lambda account: account.Account_getFormattedTitle())
return account_list
