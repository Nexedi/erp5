variation_text = context.getVariationText()
if variation_text is not None:
  destination = context.getBaobabDestination() 
  if destination is not None:
    if destination.find('encaisse_des_billets_retires_de_la_circulation')>=0:
      variation_text = variation_text.replace('cash_status/cancelled',
                                          'cash_status/retired')
return variation_text
