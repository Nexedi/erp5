# Hot reindexing reindexes all documents using destination_sql_catalog_id
# with low priority (so site can keep working during hot reindexation).

REQUEST = context.REQUEST

source_sql_catalog_id = context.getSourceSqlCatalogId()
destination_sql_catalog_id = context.getDestinationSqlCatalogId()

return context.manage_hotReindexAll(source_sql_catalog_id = source_sql_catalog_id,
                                    destination_sql_catalog_id = destination_sql_catalog_id,
                                    REQUEST=REQUEST)
