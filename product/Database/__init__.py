from contextlib import contextmanager

def configure(erp5_catalog_storage):
    from Products.Database import db, DA
    db.configure(erp5_catalog_storage)
    DA.configure(erp5_catalog_storage)

@contextmanager
def configured(erp5_catalog_storage):
    from Products.Database import db, DA
    saved_db, saved_DA = db._backend, DA._backend
    configure(erp5_catalog_storage)
    try:
        yield
    finally:
        db._backend = saved_db
        DA._backend = saved_DA
