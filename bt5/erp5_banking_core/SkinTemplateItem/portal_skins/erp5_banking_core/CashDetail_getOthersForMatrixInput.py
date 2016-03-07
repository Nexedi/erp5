request = context.REQUEST
return_value = None
if my_choice == 'emission_letter_item':
   my_list = getattr(request,'my_emission_letter_list',None)   # Find Emission letter on the REQUEST
   if my_list is None:
      my_list = getattr(request,'field_my_emission_letter_list',None)   # Find Emission letter on the REQUEST

   if my_list is not None:
      return_value =  [x for x in context.portal_categories.emission_letter.getCategoryChildTitleItemList()
                if x[1] in my_list ]
   else:
      return_value =  [x for x in context.portal_categories.emission_letter.getCategoryChildTitleItemList()]
elif my_choice == 'emission_letter_default_value':
   return_value = getattr(request,'my_emission_letter_list',None)   # Find Emission letter on the REQUEST
   return_value = return_value[1]
elif my_choice == 'cash_status_item':
   my_list = getattr(request,'my_cash_status_list',None)   # Find cash Status on the REQUEST
   if my_list is None:
      my_list = getattr(request,'field_my_cash_status_list',None)   # Find Emission letter on the REQUEST
   if my_list is not None:
      return_value =  [x for x in context.portal_categories.cash_status.getCategoryChildTranslatedTitleItemList()
                  if x[1] in my_list]
   else:
      return_value =  [x for x in context.portal_categories.cash_status.getCategoryChildTranslatedTitleItemList()]
elif my_choice == 'cash_status_default_value':
   return_value = getattr(request,'my_cash_status_list',None)   # Find cash Status on the REQUEST
   return_value = return_value[1]

elif my_choice == 'variation_item':
   my_list = getattr(request,'my_variation_list',None)   # Find variation on the REQUEST
   if my_list is None:
      my_list = getattr(request,'field_my_variation_list',None)   # Find variation on the REQUEST
   if my_list is not None:
      return_value =  [x for x in context.portal_categories.variation.getCategoryChildTitleItemList()
                  if x[1] in my_list]
   else:
      return_value =  [x for x in context.portal_categories.variation.getCategoryChildTitleItemList()]
elif my_choice == 'variation_default_value':
   return_value = getattr(request,'my_variation_list',None)   # Find variation on the REQUEST
   return_value = return_value[1]


return return_value
