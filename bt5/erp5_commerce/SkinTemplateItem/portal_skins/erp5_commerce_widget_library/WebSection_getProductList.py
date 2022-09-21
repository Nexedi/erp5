#TODO : USE CACHE
#the goal of this script is to get all the related product of this section
current_web_section = context.REQUEST.get('current_web_section', context)
product_list = []

if 'portal_type' not in kw:
  kw['portal_type'] = 'Product'
		 
if 'limit' not in kw:		 
  kw['limit'] = limit		 
		 
if 'all_versions' not in kw:		 
  kw['all_versions'] = 1		 
		 
if 'all_languages' not in kw:		 
  kw['all_languages'] = 1		 
		 
for key in ['limit','all_versions','all_languages']:		 
  kw[key] = int(kw[key])		 
		 
product_list = current_web_section.getDocumentValueList(**kw)
return product_list
