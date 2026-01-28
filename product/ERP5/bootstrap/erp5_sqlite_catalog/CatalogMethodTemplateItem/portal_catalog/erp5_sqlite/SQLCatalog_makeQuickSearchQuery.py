from erp5.component.module.Log import log
from Products.ZSQLCatalog.SQLCatalog import Query

# warn by logging (not possible use python's warn module in restricted environment)
log("'quick_search_text' and 'advanced_search_text' scriptable keys are deprecated. Use 'search_text' instead.")
return Query(search_text=value)
