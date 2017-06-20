"""
  MySQL's full text searchable key implementation.
"""
from Products.ZSQLCatalog.SQLCatalog import Query

query = Query(**{'full_text.SearchableText': value})
return query
