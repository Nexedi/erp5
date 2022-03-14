"""
  Sphinx full text searchable key implementation.
"""
from Products.ZSQLCatalog.SQLCatalog import Query

# set some global search engine defaults (XXX: use preferences?)
defaut_dict = {'mode': 'ext2', # full text search mode
               'limit': 1000,  # max number of results
              }
for key, item in list(defaut_dict.items()):
  operator = ';%s' %key
  if operator not in value and value not in ('', None):
    value = '%s%s=%s' %(value, operator, item)

query = Query(**{'sphinxse_query': value})
return query
