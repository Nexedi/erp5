from App.config import getConfiguration

kw = getConfiguration().product_config['initsite']

if kw.get('erp5_catalog_storage', 'erp5_mysql_innodb_catalog') == 'erp5_sqlite_catalog':
  from .SQLITEBase import SQLBase
  from .SQLITEBase import sort_message_key
  from .SQLITEBase import UID_SAFE_BITSIZE
  from .SQLITEBase import UID_ALLOCATION_TRY_COUNT
  from .SQLITEBase import INVOKE_ERROR_STATE
  from .SQLITEBase import DEPENDENCY_IGNORED_ERROR_STATE
else:
  from .MYSQLBase import SQLBase
  from .MYSQLBase import sort_message_key
  from .MYSQLBase import UID_SAFE_BITSIZE
  from .MYSQLBase import UID_ALLOCATION_TRY_COUNT
  from .MYSQLBase import INVOKE_ERROR_STATE
  from .MYSQLBase import DEPENDENCY_IGNORED_ERROR_STATE
