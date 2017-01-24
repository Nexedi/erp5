<dtml-let query="getattr(search_context, 'buildSQLQuery', portal_catalog.buildSQLQuery)(query=portal_catalog.getSecurityQuery(**kw), **kw)"
          selection_domain="kw.get('selection_domain', None)"
          selection_report="kw.get('selection_report', None)"
          optimizer_switch_key_list="getOptimizerSwitchKeyList()">

  <dtml-comment>
    Currently, there is no other choice to implement this method as an SQL catalog until SQLCatalog
    can support more features which are needed here. Once SQLCatalog supports those feature,
    this method should be refactored to use catalog only.

     The subquery is named catalog to prevent use another LEFT JOIN.
  </dtml-comment>

  <dtml-if "'derived_merge' in optimizer_switch_key_list">
    SET @current_optimizer_switch = @@optimizer_switch,
        @@optimizer_switch = 'derived_merge=off'
    <dtml-var sql_delimiter>
  </dtml-if>
  SELECT
    catalog.*
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
        CONCAT(CASE my_versioning.language
                   WHEN <dtml-sqlvar language type="string"> THEN '4'
                   WHEN '' THEN '3'
                   WHEN <dtml-sqlvar expr="Localizer.get_default_language() or 'en'" type="string"> THEN '2'
                   ELSE '1' END,
               my_versioning.version) AS priority
        <dtml-if "query['select_expression']">,<dtml-var "query['select_expression']"></dtml-if>
      FROM
        <dtml-in prefix="table" expr="query['from_table_list']">
          <dtml-var table_item> AS <dtml-var table_key>,
        </dtml-in>
        <dtml-if selection_domain>
          <dtml-var "portal_selections.buildSQLJoinExpressionFromDomainSelection(selection_domain)">,
        </dtml-if>
        <dtml-if selection_report>
          <dtml-var "portal_selections.buildSQLJoinExpressionFromDomainSelection(selection_report)">,
        </dtml-if>
        versioning AS my_versioning
      WHERE
        my_versioning.uid = catalog.uid
        <dtml-if "query['where_expression']">
          AND <dtml-var "query['where_expression']">
        </dtml-if>
        <dtml-if selection_domain>
          AND <dtml-var "portal_selections.buildSQLExpressionFromDomainSelection(selection_domain)">
        </dtml-if>
        <dtml-if selection_report>
          AND <dtml-var "portal_selections.buildSQLExpressionFromDomainSelection(selection_report)">
        </dtml-if>
        <dtml-if all_languages>
        <dtml-else>
          AND my_versioning.language IN (<dtml-sqlvar language type="string">, '')
        </dtml-if>

      ORDER BY
        priority DESC

    ) AS catalog

  <dtml-if "query['group_by_expression']">
    GROUP BY <dtml-var "query['group_by_expression']">
  </dtml-if>

  ORDER BY <dtml-var "query['order_by_expression'] or 'priority DESC'">

  <dtml-if "query['limit_expression']">
    LIMIT <dtml-var "query['limit_expression']">
  <dtml-else>
    LIMIT 1000
  </dtml-if>

  <dtml-if "'derived_merge' in optimizer_switch_key_list">
    <dtml-var sql_delimiter>
    SET @@optimizer_switch = @current_optimizer_switch
  </dtml-if>
</dtml-let>
