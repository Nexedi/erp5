<dtml-let
  asQuery="getattr(search_context, 'asQuery', None)"
  dummy="None if asQuery is None else kw.update({'websection_query': asQuery()})"
  security_query="getSecurityQuery(sql_catalog_id=getId(), local_roles=kw.pop('local_roles', None))"
  dummy2="None if security_query is None else kw.update({'security_query': security_query})"
  query="buildSQLQuery(**kw)"
>

SELECT
  catalog.*
FROM
(
  SELECT
    inner_catalog.*,

    ROW_NUMBER() OVER (
      PARTITION BY
        <dtml-var "query['group_by_expression'] or 'inner_catalog.uid'">
      ORDER BY
        inner_catalog.priority DESC
    ) AS rn

  FROM
  (
    SELECT
      catalog.uid,
      catalog.path,
      catalog.int_index,
      catalog.modification_date,
      catalog.reference,
      catalog.creation_date,
      catalog.title,

      (
        CASE my_versioning.language
             WHEN <dtml-sqlvar language type="string"> THEN '4'
             WHEN '' THEN '3'
             WHEN <dtml-sqlvar expr="Localizer.get_default_language() or 'en'" type="string"> THEN '2'
             ELSE '1'
        END
        || my_versioning.version
      ) AS priority

      <dtml-if "query['select_expression']">
        , <dtml-var "query['select_expression']">
      </dtml-if>

    FROM
      <dtml-in prefix="table" expr="query['from_table_list']">
        <dtml-var table_item> AS <dtml-var table_key>,
      </dtml-in>
      versioning AS my_versioning

    WHERE
      my_versioning.uid = catalog.uid

      <dtml-if "query['where_expression']">
        AND <dtml-var "query['where_expression']">
      </dtml-if>

      <dtml-if strict_language>
        AND my_versioning.language IN (
          <dtml-sqlvar language type="string">,
          ''
        )
      </dtml-if>

  ) AS inner_catalog
) AS catalog

WHERE rn = 1

ORDER BY
  <dtml-var "query['order_by_expression'] or 'priority DESC'">

<dtml-if "query['limit_expression']">
  LIMIT <dtml-var "query['limit_expression']">
</dtml-if>

</dtml-let>