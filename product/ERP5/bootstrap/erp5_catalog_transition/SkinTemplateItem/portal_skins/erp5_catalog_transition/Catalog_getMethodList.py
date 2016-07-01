# This script should always be called with context as either
# ERP5Catalog object or SQLCatalog.Catalog object

method_list = context.Catalog_getCatalogMethodIds()

method_list = [method[0] for method in method_list]
return method_list
