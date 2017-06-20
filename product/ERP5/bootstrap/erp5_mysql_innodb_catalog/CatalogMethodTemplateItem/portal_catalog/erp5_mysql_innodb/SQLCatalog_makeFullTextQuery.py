"""Entry point for full text query generation.

Delegates the query generation to full text business template, or
fallback to searching title or reference.
"""
from Products.ZSQLCatalog.SQLCatalog import ComplexQuery
from Products.ZSQLCatalog.SQLCatalog import Query

for script_name in (
  'SQLCatalog_makeSphinxSEFullTextQuery',
  'SQLCatalog_makeMroongaFullTextQuery',
  'SQLCatalog_makeMyISAMFullTextQuery'):
  script_object = getattr(container, script_name, None)
  if script_object is not None:
    return script_object(value)

query = ComplexQuery(Query(title=value),
                     Query(reference=value),
                     logical_operator="OR")
return query
