"""Guess the path of categories, taking as input a mapping {base_category:
category}, where category can be the relative_url, the title or the reference
of the category
"""

from Products.ZSQLCatalog.SQLCatalog import Query, ComplexQuery
portal = context.getPortalObject()
result_dict = {}

for base_category_name, category in category_dict.items():
  category_object = \
    context.getPortalObject().portal_categories[base_category_name]

  category_value = category_object.restrictedTraverse(category, None)
  if category_value is None:
    query = ComplexQuery(
                ComplexQuery(Query(title=category,
                               key='ExactMatch'),
                         Query(reference=category,
                               key='ExactMatch'),
                         logical_operator='OR'),
                ComplexQuery(Query(relative_url='%s/%%' % base_category_name)))
    category_value = portal.portal_catalog.getResultValue(query=query)

  if category_value is not None:
    # remove base category from relative_url
    result_dict[base_category_name] = \
      category_value.getRelativeUrl().split('/', 1)[1]

return result_dict
