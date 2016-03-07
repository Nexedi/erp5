<dtml-comment>
  Use SQL method rather that catalog to speed up searching
</dtml-comment>

<dtml-let query="buildSQLQuery(query=portal_catalog.getSecurityQuery(**kw), **kw)"          
          fix="query['from_table_list'].append(('full_text','full_text'))">

SELECT catalog.uid, 
       catalog.path, 
       catalog.portal_type, 
       catalog.title,
       catalog.reference, 
       catalog.modification_date,
       catalog.owner,
       <dtml-if is_full_text_search_on> search_results.text, </dtml-if>
       join_category.category_uid,
       join_category.base_category_uid,
       join_category.category_relative_url,
       versioning.version,
       versioning.language

FROM  catalog,
      versioning,
      (SELECT catalog.uid
              <dtml-if is_full_text_search_on>
                <dtml-if use_text_excerpts>
                /*  MySQL server can produc text excerpts */
                , sphinx_snippets(full_text.SearchableText, 'erp5', '<dtml-var "search_string">') AS text
                <dtml-else>
                /* Return all searchable text to server which will extract found text excerpts */
                , full_text.SearchableText AS text
                </dtml-if>
              </dtml-if>
              <dtml-if "query['select_expression']">
                ,<dtml-var "query['select_expression']">
              </dtml-if>
        FROM
          <dtml-in prefix="table" expr="query['from_table_list']">
            <dtml-if sequence-end>
                <dtml-var table_item> AS <dtml-var table_key>
            <dtml-else>
              <dtml-var table_item> AS <dtml-var table_key>,
            </dtml-if>
          </dtml-in>
        WHERE <dtml-var "query['where_expression']"> AND  `catalog`.`uid` = `full_text`.`uid`

        <dtml-if "query['order_by_expression']"> ORDER BY <dtml-var "query['order_by_expression']"> </dtml-if>

        <dtml-if "query['limit_expression']"> LIMIT <dtml-var "query['limit_expression']"> 
        <dtml-else> LIMIT 1000 </dtml-if>) 

        AS search_results LEFT JOIN 
          (SELECT category.uid AS join_category_uid, 
                  category.base_category_uid AS base_category_uid,
                  category.category_uid AS category_uid,
                  catalog.relative_url AS category_relative_url
            FROM category, catalog
            WHERE category.category_strict_membership = 1
                  AND category.base_category_uid IN 
                    (<dtml-in prefix="loop" expr="base_category_uid_list">
                        <dtml-if sequence-end>
                          <dtml-sqlvar expr="loop_item" type="int">
                        <dtml-else>
                          <dtml-sqlvar expr="loop_item" type="int">,
                        </dtml-if>
                      </dtml-in>)
                  AND category.category_uid = catalog.uid

            ) AS join_category
            ON search_results.uid = join_category.join_category_uid

WHERE search_results.uid = catalog.uid AND versioning.uid = catalog.uid

</dtml-let>