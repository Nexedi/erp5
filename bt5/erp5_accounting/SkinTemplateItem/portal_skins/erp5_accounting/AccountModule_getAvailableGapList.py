# Return the list of gap roots that can be used.
# gap category is typically organized such as : 
#  gap / country / gap_name
# so we always use as "root" the category of depth 2.

results = []
countries = context.portal_categories.gap.objectValues()
for country in countries : 
  for gap in country.objectValues() :
    title = gap.getParentValue().getTranslatedTitle() + '/'+ gap.getTranslatedTitle()
    path = gap.getRelativeUrl()
    if not include_gap_in_path : 
      path = path.replace('gap/', '')

    results += [(title, path)]

if include_empty_item == 1:
  results = [('', '')] + results

return results
