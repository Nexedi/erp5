"""
 Key categories for Supply Paths for Pricing Optimisation

 The way of the optimisation is reducing target supply paths,
 else all supply paths are the domain of the SELECT.
"""
category = context.portal_categories

return [(x.id, x.id) for x in (category.resource, category.source,
                               category.source_section, category.destination,
                               category.destination_section, category.source_account,
                               category.price_currency)]
