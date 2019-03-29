if context.getSource() is None:
  return None

site_letter = context.getSourceValue().getCodification()[0].lower()
site = context.Baobab_getVaultSite(context.getSource()).getRelativeUrl()
cash_status = context.getCashStatus()
# possible cash status : cancelled, to_sort, valid
emission_letter = context.getEmissionLetter()

resource_portal_type = context.getResourceValue().getPortalType()
if resource_portal_type == 'Banknote':
  if emission_letter == "not_defined":
    if cash_status == "to_sort":
      # banknote letter 'not defined' / a trier -> caisse source
      source = context.getSource()
      if not 'ventilation' in source:
        return '%s/caveau/auxiliaire/encaisse_des_billets_et_monnaies' %(site,)
      else:
        return '%s/caveau/auxiliaire/%s' %(site, '/'.join(source.split('/')[-2:]))
    else:
      # This case is/must be protected by a constraint: a document containing a
      # line matching this condition must not get validated.
      # XXX: Maybe we should return None here instead of raising.
      raise Exception('Should not be here')
  elif emission_letter == site_letter:
    if cash_status == "valid":
      # banknote 'valid' from same country -> caisse de reserve / billets et monnaies
      return '%s/caveau/reserve/encaisse_des_billets_et_monnaies' %(site,)
    else:
      # banknote of any other status from same country -> caisse auxiliaire / billets et monnaies
      return '%s/caveau/auxiliaire/encaisse_des_billets_et_monnaies' %(site,)
  elif emission_letter == "mixed":
    # banknote letter 'mixed' -> caisse auxiliaire / encaisse externe
    return '%s/caveau/auxiliaire/encaisse_des_externes' %(site,)
  else: # emission_letter != site_letter
    # external banknote  -> caisse auxiliaire / encaisse externe
    return '%s/caveau/auxiliaire/encaisse_des_externes' %(site,)
else:
  # Coin
  if cash_status == "valid":
    return '%s/caveau/reserve/encaisse_des_billets_et_monnaies' %(site,)
  else:
    return '%s/caveau/auxiliaire/encaisse_des_billets_et_monnaies' %(site,)
     
  

# if emission_letter!='not_defined' and not (emission_letter in site_letter):
#   return '%s/caveau/auxiliaire/encaisse_des_externes' %(site,)
# elif cash_status == "mixed":
#   return '%s/caveau/auxiliaire/encaisse_des_externes' %(site,)
# elif emission_letter=='not_defined':
#   # remaining banknote which are not sorted yet, or cancelled one
#   if not 'ventilation' in context.getSource():
#     return '%s/caveau/auxiliaire/encaisse_des_billets_et_monnaies' %(site,)
#   else:
#     if context.getCashStatus() in ("to_sort",):
#       return context.getSource()
#       #return '%s/caveau/auxiliaire/encaisse_des_externes' %(site,)
#     else:
#       # take classification into account here
#       source_list = context.getSource().split('/')
#       return '%s/caveau/auxiliaire/%s' %(site,'/'.join(source_list[-2:]))
# elif (context.getCashStatus() in ('to_sort', 'cancelled')) and emission_letter in site_letter:
#   return '%s/caveau/auxiliaire/encaisse_des_billets_et_monnaies' %(site,)
# elif emission_letter in site_letter:
#   return '%s/caveau/reserve/encaisse_des_billets_et_monnaies' %(site,)
# else:
#   return '%s/caveau/auxiliaire/encaisse_des_externes' %(site,)
