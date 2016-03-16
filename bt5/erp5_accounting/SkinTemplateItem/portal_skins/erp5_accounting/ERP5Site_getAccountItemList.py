'''Returns all validated accounts '''
from Products.ERP5Type.Cache import CachingMethod

portal = context.getPortalObject()

def getAccountItemList(section_category,
                       section_category_strict,
                       from_date,
                       lang):

  account_list = [('', '')]
  for account in portal.account_module.searchFolder(
                           portal_type='Account',
                           select_list=["relative_url"],
                           validation_state=('validated',)):
    account_list.append((
      account.Account_getFormattedTitle(),
      account.relative_url,))

  account_list.sort(key=lambda x: x[0])

  return account_list

getAccountItemList = CachingMethod(getAccountItemList,
                                   id=script.getId(),
                                   cache_factory='erp5_content_long')

return getAccountItemList(section_category,
                          section_category_strict,
                          lang=portal.Localizer.get_selected_language(),
                          from_date=from_date)
