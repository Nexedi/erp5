# Return the list of gap roots that can be used.
# gap category is typically organized such as :
#  gap / country / gap_name
# so we always use as "root" the category of depth 2.

item_list = [('', '')]
countries = context.portal_categories.gap.objectValues()
for country in countries:
  for gap in country.objectValues():
    path = gap.getRelativeUrl()
    item_list.append(
        ((country.getTranslatedTitle() + '/'+ gap.getTranslatedTitle()),
        path))

return item_list
