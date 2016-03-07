<dtml-let portal="getPortalObject()">
<dtml-let catalog="portal.portal_catalog.getSQLCatalog(getId())">
DELETE FROM <dtml-var expr="getattr(catalog, 'sphinx_index', getattr(portal, 'sphinx_index', 'erp5'))"> WHERE id=<dtml-sqlvar expr="uid" type=int>
</dtml-let>
</dtml-let>
