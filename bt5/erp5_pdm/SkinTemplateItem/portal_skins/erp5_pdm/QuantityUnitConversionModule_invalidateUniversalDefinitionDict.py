from Products.ERP5Type.Cache import CachingMethod
def foo(): pass
cached = CachingMethod(foo,
                       "getUniversalQuantityUnitDefinitionDict",
                       cache_factory="erp5_content_long")

cached.delete()

context.QuantityUnitConversionModule_getUniversalDefinitionDict()
