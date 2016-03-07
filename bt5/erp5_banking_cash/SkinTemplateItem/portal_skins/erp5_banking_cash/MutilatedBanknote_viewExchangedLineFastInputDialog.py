cash_detail_dict = {'line_portal_type'           : 'Exchanged Mutilated Banknote Line'
                    , 'operation_currency'       :  context.Baobab_getPortalReferenceCurrencyID()
                    , 'cash_status_list'         : ['to_sort',]
                    , 'emission_letter_list'     : ['not_defined',]
                    , 'variation_list'           :  context.Baobab_getResourceVintageList(banknote=1)
                    , 'currency_cash_portal_type': 'Banknote'
                    , 'read_only'                : False
                    , 'column_base_category'     : 'variation'
                    }

return context.CashDelivery_generateCashDetailInputDialog(listbox = None
                                                          , cash_detail_dict = cash_detail_dict
                                                          , destination = context.getObject().absolute_url()
                                                          , target_total_price = context.getDestinationTotalAssetPrice())
