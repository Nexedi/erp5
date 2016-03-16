search_method = getattr(context, 'getDocumentValueList',
                        context.getPortalObject().portal_catalog)
return search_method(**kw)
