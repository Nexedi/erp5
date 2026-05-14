from contextlib import contextmanager

def configure(erp5_catalog_storage):
    from Products.Database import db, DA
    db.configure(erp5_catalog_storage)
    DA.configure(erp5_catalog_storage)

@contextmanager
def configured(erp5_catalog_storage):
    from Products.Database import db, DA
    saved_db = dict(vars(db))
    saved_DA = dict(vars(DA))
    configure(erp5_catalog_storage)
    try:
        yield
    finally:
        for _m, _saved in ((db, saved_db), (DA, saved_DA)):
            _d = vars(_m)
            for _k in list(_d):
                if _k not in _saved:
                    del _d[_k]
            _d.update(_saved)
