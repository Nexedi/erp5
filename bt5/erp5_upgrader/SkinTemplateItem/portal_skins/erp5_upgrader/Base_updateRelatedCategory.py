portal = context.getPortalObject()
updateRelatedCategory = portal.portal_categories.updateRelatedCategory

new_category_list = []
object_category_list = context.getCategoriesList()

new_category_name = kw['new_category_name']
old_category_name = kw['old_category_name']

for category in object_category_list:
  new_category = updateRelatedCategory(category, old_category_name, new_category_name)
  new_category_list.append(new_category)

if new_category_list != object_category_list:
  context.setCategoriesList(new_category_list)
