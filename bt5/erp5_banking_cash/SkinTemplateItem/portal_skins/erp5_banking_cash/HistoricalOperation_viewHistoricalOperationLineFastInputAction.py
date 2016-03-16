cash_detail_dict = {'line_portal_type'          : 'Cash Delivery Line'
                    , 'operation_currency'       : context.Baobab_getPortalReferenceCurrencyID()
                    , 'cash_status_list'          : ['valid', 'new_not_emitted', 'new_emitted', 'not_defined', 'cancelled']
                    , 'emission_letter_list'      : None
                    #, 'emission_letter_list'      : #  context.Baobab_getUserEmissionLetterList()
                    , 'variation_list'           : context.Baobab_getResourceVintageList(coin=1, banknote=1)
                    , 'currency_cash_portal_type'  :  None
                    , 'read_only'           : False
                    , 'column_base_category'               : 'variation'
                    }

return context.CashDelivery_generateCashDetailInputDialog(listbox = None
                                                          , cash_detail_dict = cash_detail_dict
                                                          , destination = context.getObject().absolute_url())
