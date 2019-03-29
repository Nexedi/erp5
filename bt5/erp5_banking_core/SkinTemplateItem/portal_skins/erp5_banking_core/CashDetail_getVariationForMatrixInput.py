request = context.REQUEST
default_emission_letter_list = getattr(request,'my_emission_letter_list',None)       # Find Emission letter on the REQUEST
default_cash_status_list     = getattr(request,'my_cash_status_list',None)           # Find Cash Status on the REQUEST
default_variation_list      = getattr(request,'my_variation_list',None)            # Find Variation on the REQUEST
default_other_parameter_list      = getattr(request,'my_other_parameter',None)            # Find Variation on the REQUEST


return_list = []
return_list.append(['displayed_resource','Resource'])


if default_emission_letter_list is None:
   default_emission_letter_list = getattr(request,'field_my_emission_letter_list',[])       # Find Emission letter on the REQUEST
   default_cash_status_list     = getattr(request,'field_my_cash_status_list',[])           # Find Cash Status on the REQUEST
   default_variation_list      = getattr(request,'field_my_variation_list',[])            # Find Variation on the REQUEST
   default_other_parameter_list = getattr(request,'field_my_other_parameter', [])            # Find Variation on the REQUEST


if len(default_other_parameter_list) > 2:
   default_column_base = default_other_parameter_list[3]
else :
   default_column_base = 'variation'

allow_add_line = False
if len(default_emission_letter_list) > 1 and default_column_base != 'emission_letter':
   return_list.append(['emission_letter','Emission Letter'])
   allow_add_line = True
if len(default_cash_status_list) > 1 and default_column_base != 'cash_status':
   return_list.append(['cash_status','Cash Status'])
   allow_add_line = True
if len(default_variation_list) > 1 and default_column_base != 'variation':
   return_list.append(['variation','Variation'])
   allow_add_line = True

if allow_add_line:
   return_list.append(['number_line_to_add','Lines To Add'])


if default_column_base == 'cash_status':
   default_column_base_list = default_cash_status_list
   column_category  = 'cash_status'
elif default_column_base == 'emission_letter':
   default_column_base_list = default_emission_letter_list
   column_category  = 'emission_letter'
else:
   default_column_base_list = default_variation_list
   column_category  = 'variation'



if len(default_column_base_list) > 0 :
   column_base_list =  [x for x in context.portal_categories[column_category].getCategoryChildTitleItemList()[1:]
                        if x[1] in default_column_base_list]
else:
   column_base_list =  context.portal_categories[column_category].getCategoryChildTitleItemList()[1:]



counter = 1
for x in column_base_list:
   return_list.append(['column'+str(counter),x[0]])
   counter += 1
return_list.append(['price','Price'])
return_list.append(['resource_id','Resource'])
return return_list
