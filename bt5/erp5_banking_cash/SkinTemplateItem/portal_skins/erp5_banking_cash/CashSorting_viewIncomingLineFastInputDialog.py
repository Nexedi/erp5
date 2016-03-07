cash_detail_dict = {'line_portal_type'           : 'Incoming Cash Sorting Line'
                    , 'operation_currency'       :  context.Baobab_getPortalReferenceCurrencyID()
                    , 'cash_status_list'         : ['to_sort','valid','cancelled','mutilated']
                    , 'emission_letter_list'     : None
                    , 'variation_list'           :  context.Baobab_getResourceVintageList(banknote=1, coin=1)
                    , 'currency_cash_portal_type': None
                    , 'read_only'                : False
                    , 'column_base_category'     : 'variation'
                    }

return context.CashDelivery_generateCashDetailInputDialog(listbox = None
                                                          , cash_detail_dict = cash_detail_dict
                                                          , destination = context.getObject().absolute_url())
