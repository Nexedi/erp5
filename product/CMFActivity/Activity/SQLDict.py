from App.config import getConfiguration

kw = getConfiguration().product_config['initsite']

if kw.get('erp5_catalog_storage', 'erp5_mysql_innodb_catalog') == 'erp5_sqlite_catalog':
  from .SQLITEDict import SQLDict
else:
  from .MYSQLDict import SQLDict