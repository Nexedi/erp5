<dtml-let portal="getPortalObject()">
<dtml-let catalog="portal.portal_catalog.getSQLCatalog(getId())">
REPLACE INTO
  <dtml-var expr="getattr(catalog, 'sphinx_index', getattr(portal, 'sphinx_index', 'erp5'))">
VALUES
<dtml-in prefix="loop" expr="_.range(_.len(uid))">
(
  <dtml-sqlvar expr="uid[loop_item]" type="int">,
  <dtml-sqlvar expr="(SearchableText[loop_item] or '')" type="string">,
  <dtml-sqlvar expr="uid[loop_item]" type="int">
)
<dtml-if sequence-end>
<dtml-else>
,
</dtml-if>
</dtml-in>
</dtml-let>
</dtml-let>