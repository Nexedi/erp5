request = context.REQUEST

source = context.getSource()
currency = context.Baobab_getPortalReferenceCurrencyID()
source_section = context.getSourceSection()

if source is None:
  redirect_url = '%s/%s?%s' % ( context.absolute_url()
                                , 'view'
                                , 'portal_status_message=Please+select+a+source.'
                                )
  return request.RESPONSE.redirect( redirect_url )


if 'serre' in source:
  cash_status = ['retired','error']
else:
  cash_status = ['cancelled','mutilated', 'maculated','error']

# Select the emission letter of the remote site if there is one defined
if source_section is None:
  emission_letter = context.Baobab_getUserEmissionLetterList() 
else:
  emission_letter = list((context.getSourceSectionValue().getCodification()[0]).lower())


variation = context.Baobab_getResourceVintageList(banknote=1, coin=1)

#, 'emission_letter_list'     : emission_letter A REMETTRE APRES LES TESTS
cash_detail_dict = {'line_portal_type'           : 'Monetary Destruction Line'
                    , 'operation_currency'       : currency
                    , 'cash_status_list'         : cash_status
                    , 'emission_letter_list'      : emission_letter
                    , 'variation_list'           : variation
                    , 'currency_cash_portal_type': None
                    , 'read_only'                : False
                    , 'column_base_category'     : 'variation'
                    }

return context.CashDelivery_generateCashDetailInputDialog(listbox = None
                                                          , cash_detail_dict = cash_detail_dict
                                                          , destination = context.getObject().absolute_url()
                                                          )
