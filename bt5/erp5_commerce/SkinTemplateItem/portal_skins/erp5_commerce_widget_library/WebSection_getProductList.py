#TODO : USE CACHE
#the goal of this script is to get all the related product of this section
current_web_section = context.REQUEST.get('current_web_section', context)
product_list = []

if not kw.has_key('portal_type'):
  kw['portal_type'] = 'Product'
		 
if not kw.has_key('limit'):		 
  kw['limit'] = limit		 
		 
if not kw.has_key('all_versions'):		 
  kw['all_versions'] = 1		 
		 
if not kw.has_key('all_languages'):		 
  kw['all_languages'] = 1		 
		 
for key in ['limit','all_versions','all_languages']:		 
  kw[key] = int(kw[key])		 
		 
product_list = current_web_section.getDocumentValueList(**kw)
return product_list
