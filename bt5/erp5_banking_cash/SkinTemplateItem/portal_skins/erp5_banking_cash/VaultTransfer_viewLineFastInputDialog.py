request = context.REQUEST
currency = context.getResourceId()

if currency is None :
  redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , 'view'
                              , 'portal_status_message=Please+select+a+currency.'
                              )
  return request.RESPONSE.redirect( redirect_url )

if currency != context.Baobab_getPortalReferenceCurrencyID():
  cash_status = ['valid']
  emission_letter = ['not_defined']
  variation = ['not_defined']
else:
  cash_status = None
  emission_letter = None
  variation = context.Baobab_getResourceVintageList(banknote=1, coin=1)

cash_detail_dict = {'line_portal_type'           : 'Vault Transfer Line'                #'Cash Delivery Line'
                    , 'operation_currency'       : currency
                    , 'cash_status_list'         : cash_status
                    , 'emission_letter_list'     : emission_letter
                    , 'variation_list'           : variation
                    , 'currency_cash_portal_type': None
                    , 'read_only'                : False
                    , 'column_base_category'     : 'variation'
                    }

return context.CashDelivery_generateCashDetailInputDialog(listbox = None
                                                          , cash_detail_dict = cash_detail_dict
                                                          , destination = context.getObject().absolute_url()
                                                          )
