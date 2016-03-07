SET @current_path = NULL; <dtml-var sql_delimiter>
SET @current_reference = NULL; <dtml-var sql_delimiter>

<dtml-let query="portal_catalog.buildSQLQuery(query=portal_catalog.getSecurityQuery(), portal_type=getPortalDocumentTypeList())">
<dtml-let user_language="Localizer.get_selected_language()">

SELECT path, uid
FROM
(
SELECT DISTINCT
path,
(select uid from catalog where catalog.path=sub.path) as uid
FROM
( SELECT
    @current_path:=IF(@current_reference = reference, @current_path, path) AS path,
    @current_reference:=reference AS reference
  FROM (
    SELECT
      reference,
      path,
      catalog.uid,
      CASE language WHEN <dtml-sqlvar user_language type=string> THEN 1 WHEN 'en' THEN 0 ELSE -1 END as language_order
    FROM
      catalog, versioning, sphinxse_index
    WHERE
      catalog.uid = versioning.uid
      AND
        catalog.uid = sphinxse_index.uid
      <dtml-if "query['where_expression']">
      AND <dtml-var "query['where_expression']">
      </dtml-if>
      AND
        sphinxse_index.sphinxse_query="<dtml-sqlvar reference type=string>;mode=ext2"
      AND
        <dtml-sqltest reference op=ne type=string>
    ORDER BY reference, language_order DESC, version DESC, revision DESC
  ) AS innersub
)
AS sub
)
AS main
WHERE
<dtml-sqltest "getUid()" column=uid op=ne type=int>
LIMIT 1000

</dtml-let>
</dtml-let>
