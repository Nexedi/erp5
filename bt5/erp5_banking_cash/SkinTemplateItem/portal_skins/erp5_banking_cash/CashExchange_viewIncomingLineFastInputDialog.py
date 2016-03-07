request = context.REQUEST
a = 1
cash_status = ['to_sort']
cash_detail_dict = { 'line_portal_type'            : 'Incoming Cash Exchange Line'             # The portal type that the fastinput will create
                     , 'operation_currency'        : 'XOF'                          # The operation currently
                     , 'cash_status_list'          : cash_status                    # List of possible cashStatus or None if all
                     , 'emission_letter_list'      : ['not_defined',]                # List of possible emissionLetter or None if all
                     , 'variation_list'            : context.Baobab_getResourceVintageList(banknote=1, coin=1)      # List of possible variation or None if all      #['2003']                       # List of possible variation or None if all
                     , 'currency_cash_portal_type' : None                           # 'Coin' or 'Banknote' or None if both
                     , 'read_only'                 : False                           # If true, the fastinput will not allow change
                     , 'column_base_category'      : 'variation'                    # possible values : 'variation', 'cashStatus', 'emissionLetter'
}



return context.CashDelivery_generateCashDetailInputDialog(listbox = None
                                                          , cash_detail_dict = cash_detail_dict
                                                          , destination = context.getObject().absolute_url())
