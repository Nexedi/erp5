request = context.REQUEST
source = context.getSource()
source_section = context.getSourceSection()

cash_status = ['to_sort']
emission_letter = ['not_defined']
variation = context.Baobab_getResourceVintageList(banknote=1, coin=1)

cash_detail_dict = {'line_portal_type'           : 'Incoming Cash To Currency Sale Line'
                    , 'operation_currency'       : context.Baobab_getPortalReferenceCurrencyID()
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
                                                          , target_total_price = context.getQuantity()
                                                          )
