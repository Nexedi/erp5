## Script (Python) "identify_category"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=base_category='', category=''
##title=
##
# returns the uid of the category object
# according to the given base_category string and category string

category_items = category.split("/")
category_object = context.portal_categories[base_category]

for item in category_items :
  category_object=category_object[item]

return category_object.uid
