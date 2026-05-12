def configure(erp5_catalog_storage):
    from . import SQLBase
    SQLBase.configure(erp5_catalog_storage)
    from . import SQLDict, SQLJoblib, SQLQueue
    SQLDict.configure(erp5_catalog_storage)
    SQLJoblib.configure(erp5_catalog_storage)
    import Products.CMFActivity.ActivityTool as ActivityTool
    ActivityTool.activity_dict = {
        k: getattr(v, k)()
        for k, v in {'SQLDict': SQLDict, 'SQLQueue': SQLQueue, 'SQLJoblib': SQLJoblib}.items()}
