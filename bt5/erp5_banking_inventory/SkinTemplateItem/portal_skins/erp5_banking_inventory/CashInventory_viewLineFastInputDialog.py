request = context.REQUEST
currency_id = context.getPriceCurrencyId()
vault = context.getDestination()

redirect_url = None
if currency_id in (None, ''):
  redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , 'view'
                              , 'portal_status_message=Please+specify+a+currency.'
                              )
if vault in (None, ''):
  redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , 'view'
                              , 'portal_status_message=Please+specify+a+destination+vault.'
                              )
if redirect_url is not None:
  return request.RESPONSE.redirect(redirect_url)


if currency_id == context.Baobab_getPortalReferenceCurrencyID():
  letter_list      = None
  variation_list   = context.Baobab_getResourceVintageList(coin=1, banknote=1)
  cash_status_list = None
else:
  letter_list      = ['not_defined']
  variation_list   = ['not_defined']
  cash_status_list = ['not_defined']

cash_detail_dict = {'line_portal_type'           : 'Cash Inventory Line'
                    , 'operation_currency'       : context.getPriceCurrencyId()
                    , 'cash_status_list'         : cash_status_list
                    , 'emission_letter_list'     : letter_list
                    , 'variation_list'           : variation_list
                    , 'currency_cash_portal_type': None
                    , 'read_only'                : False
                    , 'column_base_category'     : 'variation'
                    , 'use_inventory'            : False
                    }

return context.CashDelivery_generateCashDetailInputDialog( listbox              = None
                                         , cash_detail_dict = cash_detail_dict
                                         , destination          = context.getObject().absolute_url())
