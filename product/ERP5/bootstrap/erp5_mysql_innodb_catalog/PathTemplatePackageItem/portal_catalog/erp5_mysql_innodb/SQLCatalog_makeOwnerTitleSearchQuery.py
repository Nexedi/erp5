from Products.ZSQLCatalog.SQLCatalog import SimpleQuery

portal = context.getPortalObject()

reference_list = [x.reference for x in
                  portal.portal_catalog(SimpleQuery(reference=None,
                                                    comparison_operator="is not"),
                                        select_list=['reference'],
                                        portal_type="Person", title=value)]

return SimpleQuery(owner=reference_list or value or -1)
