import os

erp5_catalog_storage = os.environ.get('erp5_catalog_storage', 'erp5_mysql_catalog')

if erp5_catalog_storage == 'erp5_sqlite_catalog':
  from .SQLITEJoblib import SQLJoblib
else:
  from .MYSQLJoblib import SQLJoblib