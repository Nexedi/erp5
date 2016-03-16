cash_detail_dict = {'line_portal_type'           : 'Cash Delivery Line'
                    , 'operation_currency'       : context.Baobab_getPortalReferenceCurrencyID()
                    , 'cash_status_list'         : ['new_not_emitted',]
                    , 'emission_letter_list'     : ['not_defined',]
                    , 'variation_list'           : context.Baobab_getResourceVintageList(coin=1)
                    , 'currency_cash_portal_type': ['Coin',]
                    , 'read_only'                : False
                    , 'column_base_category'     : 'variation'
                    }

return context.CashDelivery_generateCashDetailInputDialog(listbox = None
                                                          , cash_detail_dict = cash_detail_dict
                                                          , destination = context.getObject().absolute_url()
                                                          , target_total_price = None
                                                          )
