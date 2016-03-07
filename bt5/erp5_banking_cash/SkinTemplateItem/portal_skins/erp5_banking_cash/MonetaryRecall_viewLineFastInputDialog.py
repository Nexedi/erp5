from Products.Formulator.Errors import ValidationError, FormValidationError
portal = context.getPortalObject()
N_ = portal.Base_translateString
request = context.REQUEST

currency = context.Baobab_getPortalReferenceCurrencyID()

#source = context.getSource()
#if 'auxiliaire/encaisse_des_billets_et_monnaies' not in source:
#  message = N_("Please select a good source.")
#  redirect_url = '%s/%s?portal_status_message=%s' % ( context.absolute_url()
#                              , 'view'
#                              , message
#                              )
 # request[ 'RESPONSE' ].redirect( redirect_url )
 
cash_status = ['cancelled','mutilated','error']
emission_letter = context.Baobab_getUserEmissionLetterList() 
variation = context.Baobab_getResourceVintageList(banknote=1, coin=1)
cash_detail_dict = {'line_portal_type'           : 'Monetary Recall Line'
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
