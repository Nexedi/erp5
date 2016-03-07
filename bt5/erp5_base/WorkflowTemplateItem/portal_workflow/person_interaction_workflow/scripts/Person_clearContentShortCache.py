# XXX-Luke: Seb pointed out that this is very bad idea to clear cache.
document = state_change['object']
if document.getReference() is not None:
  cache_tool = document.getPortalObject().portal_caches
  cache_tool.clearCache(cache_factory_list=('erp5_content_short', ),
                        before_commit=True)
