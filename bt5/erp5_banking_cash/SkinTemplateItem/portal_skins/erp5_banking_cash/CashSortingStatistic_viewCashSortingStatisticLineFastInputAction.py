cash_detail_dict = {'line_portal_type'          : 'Cash Delivery Line'
                    , 'operation_currency'       : context.Baobab_getPortalReferenceCurrencyID()
                    , 'cash_status_list'          : ['valid']
                    , 'emission_letter_list'      : None
                    , 'variation_list'           : context.Baobab_getResourceVintageList(banknote=1)
                    , 'currency_cash_portal_type'  :  None
                    , 'read_only'           : False
                    , 'column_base_category'               : 'variation'
                    , 'check_float'               : 0
                    }

return context.CashDelivery_generateCashDetailInputDialog(listbox = None
                                                          , cash_detail_dict = cash_detail_dict
                                                          , destination = context.getObject().absolute_url()
                                                          , target_total_price = None)
