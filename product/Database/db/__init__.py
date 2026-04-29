import sys
import importlib

_BACKENDS = {
    'erp5_mysql_innodb_catalog': 'Products.ZMySQLDA.db',
    'erp5_sqlite_catalog':       'Products.ZSQLiteDA.db',
}

_current_backend = None

def configure(erp5_catalog_storage):
    global _current_backend
    if _current_backend == erp5_catalog_storage:
        return
    mod = _BACKENDS.get(erp5_catalog_storage)
    if mod is None:
        raise ImportError("Unsupported DB type %s" % erp5_catalog_storage)
    backend = importlib.import_module(mod)
    this = sys.modules[__name__]
    for attr in dir(backend):
        if not attr.startswith('_'):
            setattr(this, attr, getattr(backend, attr))
    _current_backend = erp5_catalog_storage

