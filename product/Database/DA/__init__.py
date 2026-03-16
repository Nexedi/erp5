import os
import importlib
from zLOG import LOG

erp5_catalog_storage = os.environ.get('erp5_catalog_storage', 'erp5_mysql_innodb_catalog')



if erp5_catalog_storage == "erp5_mysql_innodb_catalog":
    backend_module = "Products.ZMySQLDA.DA"
elif erp5_catalog_storage == "erp5_sqlite_catalog":
    backend_module = "Products.ZSQLiteDA.DA"
else:
    raise ImportError(f"Unsupported DB type {erp5_catalog_storage}")

_backend = importlib.import_module(backend_module)

for attr in dir(_backend):
    if not attr.startswith("_"):
        globals()[attr] = getattr(_backend, attr)
