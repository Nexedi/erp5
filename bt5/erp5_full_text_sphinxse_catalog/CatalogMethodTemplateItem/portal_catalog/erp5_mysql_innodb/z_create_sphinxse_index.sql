<dtml-let portal="getPortalObject()">
<dtml-let catalog="portal.portal_catalog.getSQLCatalog(getId())">
CREATE TABLE `sphinxse_index` (
  `uid` BIGINT UNSIGNED NOT NULL,
  `weight` INTEGER NOT NULL,
  `sphinxse_query` VARCHAR(3072) NOT NULL,
  INDEX(sphinxse_query)
) ENGINE=SPHINX CONNECTION='sphinx://<dtml-var expr="getattr(catalog, 'sphinx_address', getattr(portal, 'sphinx_address', '127.0.0.1'))">:<dtml-var expr="getattr(catalog, 'sphinx_port', getattr(portal, 'sphinx_port', 9312))">/<dtml-var expr="getattr(catalog, 'sphinx_index', getattr(portal, 'sphinx_index', 'erp5'))">'
</dtml-let>
</dtml-let>
