def configure(erp5_catalog_storage):
    from Products.Database import db, DA
    db.configure(erp5_catalog_storage)
    DA.configure(erp5_catalog_storage)
