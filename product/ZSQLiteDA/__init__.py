from . import DA

misc_=DA.misc_

def initialize(context):

    context.registerClass(
        DA.Connection,
        permission="Add Z SQLite Database Connections",
        constructors=(DA.manage_addZSQLiteConnectionForm,
                      DA.manage_addZSQLiteConnection),
    )
    import Products
    Products.meta_types += dict(Products.meta_types[-1],
        name=DA.DeferredConnection.meta_type,
        action=None),
