CashMovement_cashDetail_parameter = { 'line_portalType'     : 'Cash Movement Line'
, 'operation_currency'  : 'EUR'
, 'variation_list'      : None
, 'cashStatus_list'     : ['not_defined']
, 'emissionLetter_list' : None
}

CashMovement_cashDetail_parameter = { 'line_portalType' : 'Cash Movement Line'             # The portal type that the fastinput will create
, 'operation_currency'       : context.Baobab_getPortalReferenceCurrencyID()                      # The operation currency
, 'cashStatus_list'          : None                       # List of possible cashStatus or None if all
, 'emissionLetter_list'      : None                       # List of possible emissionLetter or None if all
, 'variation_list'           : None                       # List of possible variation or None if all
, 'currencyCash_portalType'  : None                       # 'Coin' or 'Banknote' or None if both
, 'updatePossible'           : True                       # If true, the fastinput will not allow change
, 'columnBase'               : 'variation'                # possible values : 'variation', 'cashStatus', 'emissionLetter'
#, 'columnBase'              : 'emissionLetter'           # possible values : 'variation', 'cashStatus', 'emissionLetter'
#, 'columnBase'              : 'cashStatus'               # possible values : 'variation', 'cashStatus', 'emissionLetter'
}




return context.CashDetail_fastInputUpdate( listbox = None
                                   , cashDetail_parameter = CashMovement_cashDetail_parameter
                                   , destination = context.getObject().absolute_url())
