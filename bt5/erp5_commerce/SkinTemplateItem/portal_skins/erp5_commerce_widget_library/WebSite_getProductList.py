#TODO : USE CACHE
# The goal of this script is to get all the products from all the visible Web Sections
# and it must select randomly which product must be displayed for a given context.
from random import choice

web_site = context.getWebSiteValue() or context.REQUEST.get('current_web_site')

if 'portal_type' not in kw:	 	
  kw['portal_type'] = 'Product'

# Getting all the products from all the visible Web Section.
product_dict = {}
for web_section in web_site.WebSite_getMainSectionList():
  for product in web_section.getDocumentValueList(all_versions=1, all_languages=1, **kw):
    product_dict[product.uid] = product

if len(product_dict) > limit:
  random_uid_list = []
  key_list = list(product_dict.keys())
  while len(random_uid_list) < limit:
    random_uid = choice(key_list)
    key_list.remove(random_uid)
    random_uid_list.append(random_uid)
  product_list = [product_dict.get(uid) for uid in random_uid_list]
else:
  product_list = list(product_dict.values())

return product_list
