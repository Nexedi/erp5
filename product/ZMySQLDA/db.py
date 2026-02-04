import os

erp5_catalog_storage = os.environ.get('erp5_catalog_storage', 'erp5_mysql_catalog')

if erp5_catalog_storage == 'erp5_sqlite_catalog':
  from .sqlite import OperationalError
  from .sqlite import DeferredSqliteDB as DeferredDB
  from .sqlite import SqliteDB as DB
  from .sqlite import hosed_connection
else:
  from .mysql import OperationalError
  from .mysql import DeferredMysqlDB as DeferredDB
  from .mysql import MysqlDB as DB
  from .mysql import hosed_connection

