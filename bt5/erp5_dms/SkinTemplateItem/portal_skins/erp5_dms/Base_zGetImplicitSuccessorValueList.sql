<dtml-let query="portal_catalog.buildSQLQuery(query=portal_catalog.getSecurityQuery(), portal_type=getPortalDocumentTypeList())"
          user_language="Localizer.get_selected_language()"
          optimizer_switch_key_list="portal_catalog.getSQLCatalog().getOptimizerSwitchKeyList()">
<dtml-if "'derived_merge' in optimizer_switch_key_list">
  SET @current_optimizer_switch = @@optimizer_switch,
      @@optimizer_switch = 'derived_merge=off'
  <dtml-var sql_delimiter>
</dtml-if>
SET @current_path = NULL,
    @current_reference = NULL
<dtml-var sql_delimiter>
SELECT path, uid
FROM
(
SELECT DISTINCT
sub.path,
uid
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
      catalog, versioning
    WHERE
      catalog.uid = versioning.uid
      <dtml-if "query['where_expression']">
      AND <dtml-var "query['where_expression']">
      </dtml-if>
      AND
        (
         <dtml-in reference_list>
           <dtml-sqltest "_['sequence-item']" column=reference op=eq type=string>
           <dtml-unless sequence-end> OR </dtml-unless>
         </dtml-in>
        )
    ORDER BY reference, language_order DESC, version DESC, revision DESC
  ) AS innersub
)
AS sub inner join catalog on catalog.path = sub.path
)
AS main
WHERE
<dtml-sqltest "getUid()" column=uid op=ne type=int>

<dtml-if "query['limit_expression']">
  LIMIT <dtml-var "query['limit_expression']">
</dtml-if>


<dtml-if "'derived_merge' in optimizer_switch_key_list">
  <dtml-var sql_delimiter>
  SET @@optimizer_switch = @current_optimizer_switch
</dtml-if>
</dtml-let>
