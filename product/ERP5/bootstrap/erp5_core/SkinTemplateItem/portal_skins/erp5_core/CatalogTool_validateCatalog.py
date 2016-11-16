portal = context.getPortalObject()
portal_catalog = portal.portal_catalog

for i in range(101, 164):
  catalog_id = 'erp5_mysql_innodb%s'%i
  catalog = getattr(portal_catalog, catalog_id)
  if catalog.getValidationState() != 'validated':
    catalog.validate()
