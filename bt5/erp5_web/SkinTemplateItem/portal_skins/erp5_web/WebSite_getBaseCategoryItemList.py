result = []

for base_category in context.portal_categories.contentValues():
  if base_category.objectIds():
    result.append((base_category.getTranslatedTitleOrId(), base_category.getId()))

return result
