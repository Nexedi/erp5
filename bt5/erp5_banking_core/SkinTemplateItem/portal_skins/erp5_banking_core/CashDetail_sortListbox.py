def sortLine(a_Source,b_Source):
   #listContain can take 'None' , 'E' : List contain "Emission Letter", 'C': List contain "Cash Status" or 'B' : Both off them
   listContain = default_listContain
   if (a_Source['resourceId'] == a_Source['resourceId']) or (listContain is not None):
      if listContain == 'C' or listContain == 'B':
         if a_Source[cashStatus] > b_Source[cashStatus]:
            return -1
         elif a_Source[cashStatus] < b_Source[cashStatus]:
            return 0
         else:
           if listContain == 'C':
              return -1
           else:
              listContain = 'E'
      if listContain == 'E':
         if a_Source[emissionLetter] >= b_Source[emissionLetter]:
            return -1
         else :
            return 0
   elif a_Source['listbox_key'] > b_Source['listbox_key']:
      return -1
   else:
      return 0


listCurrency.sort(sortLine)
return listCurrency
