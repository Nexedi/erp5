def sortLine(a_Source,b_Source):
   if a_Source.getPortalType() in ('Coin', 'Banknote'):
      a = a_Source
      b = b_Source
   else :
      a = a.getResourceValue()
      b = b.getResourceValue()
   if a.getPortalType() == b.getPortalType() :
      if a.getPrice() > b.getPrice() :
         return -1
      elif a.getPrice() < b.getPrice() :
         return 1
      else :
         if int(a.getVariation()) < int(b.getVariation()) :
            return 1         
         elif int(a.getVariation()) > int(b.getVariation()) :
            return -1
         else :
            return 0
   elif a.getPortalType() == 'Banknote':
      return -1
   else:
      return 1


listCurrency.sort(sortLine)
return listCurrency
