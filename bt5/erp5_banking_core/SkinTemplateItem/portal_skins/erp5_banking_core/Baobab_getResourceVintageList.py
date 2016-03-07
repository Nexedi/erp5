from Products.ERP5Type.Cache import CachingMethod

def getResourceVintageList(banknote=0, coin=0):
    variation_list = {}
    if banknote and not coin:
     portal_type_list = ["Banknote",]
    elif coin and not banknote:
     portal_type_list = ["Coin",]
    else:
      portal_type_list = ["Banknote", "Coin"]

    for resource in context.currency_cash_module.objectValues():
      #context.log("Baobab_getResourcevintageList", "resource.getPriceCurrency() = %s, resource.getPortalType() = %s, portal_type_list = %s" %(resource.getPriceCurrency(),resource.getPortalType(), portal_type_list))
      if resource.getPriceCurrency() ==  "currency_module/%s" %(context.Baobab_getPortalReferenceCurrencyID(),) and resource.getPortalType() in portal_type_list:
        for variation in resource.getVariationList():
          variation_list[variation] = 1
    #context.log("variation_list", variation_list)
    return variation_list.keys()


getResourceVintageList = CachingMethod(getResourceVintageList, 
                                       id='Baobab_getResourceVintageList', 
                                       cache_factory="erp5_ui_long")

return getResourceVintageList(banknote, coin)
