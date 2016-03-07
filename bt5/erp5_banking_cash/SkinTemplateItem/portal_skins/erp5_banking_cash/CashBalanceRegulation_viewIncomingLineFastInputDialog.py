request = context.REQUEST

currency = context.getResourceId()
vcurrency = context.getResource()

if vcurrency is None :
  redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , 'view'
                              , 'portal_status_message=Please+select+a+currency.'
                              )
  return request.RESPONSE.redirect( redirect_url )

if currency != 'XOF':
  cashStatus = ['valid']
  emissionLetter = ['not_defined']
  variation = ['not_defined']
else:
  cashStatus = ['valid', 'cancelled', 'to_sort', 'new_emitted','mutilated','error']
  emissionLetter = None
  variation = context.Baobab_getResourceVintageList(banknote=1, coin=1)

cash_detail_dict= { 'line_portal_type'          : 'Incoming Cash Balance Regulation Line'        # The portal type that the fastinput will create
                    , 'operation_currency'       : currency                            # The operation currently
                    , 'cash_status_list'          : cashStatus                      # List of possible cashStatus or None if all
                    , 'emission_letter_list'      : emissionLetter                                       # List of possible emissionLetter or None if all
                    , 'variation_list'           : variation      # List of possible variation or None if all
                    , 'currency_cash_portal_type': None                                                   # 'Coin' or 'Banknote' or None if both
                    , 'read_only'           : False                          # If true, the fastinput will not allow change
                    , 'column_base_category'     : 'variation'                    # possible values : 'variation', 'cashStatus', 'emissionLetter'
                 }

return context.CashDelivery_generateCashDetailInputDialog(listbox = None
                                                          , cash_detail_dict = cash_detail_dict
                                                          , destination = context.getObject().absolute_url())
