"""
  Default full text searchable key implementation.
"""
from Products.ZSQLCatalog.SQLCatalog import ComplexQuery
from Products.ZSQLCatalog.SQLCatalog import Query

query = ComplexQuery(Query(title=value),
                     Query(reference=value),
                     operator="OR")
return query
