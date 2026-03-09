_backend = None

def configure(erp5_catalog_storage):
    global _backend
    if erp5_catalog_storage == 'erp5_mysql_innodb_catalog':
        from Products.ZMySQLDA import DA as _backend
    elif erp5_catalog_storage == 'erp5_sqlite_catalog':
        from Products.ZSQLiteDA import DA as _backend
    else:
        raise ImportError("Unsupported DA type %s" % erp5_catalog_storage)

def __getattr__(name):
    return getattr(_backend, name)
