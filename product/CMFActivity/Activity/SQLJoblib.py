import sys as _sys

_backend = None

def configure(erp5_catalog_storage):
    global _backend
    if erp5_catalog_storage == 'erp5_mysql_innodb_catalog':
        from Products.CMFActivity.Activity import MySQLJoblib as _backend
    elif erp5_catalog_storage == 'erp5_sqlite_catalog':
        from Products.CMFActivity.Activity import SQLiteJoblib as _backend
    else:
        raise ImportError("Unsupported storage %s" % erp5_catalog_storage)
    _m = _sys.modules[__name__]
    for _k, _v in vars(_backend).items():
        if not _k.startswith('_'):
            setattr(_m, _k, _v)
