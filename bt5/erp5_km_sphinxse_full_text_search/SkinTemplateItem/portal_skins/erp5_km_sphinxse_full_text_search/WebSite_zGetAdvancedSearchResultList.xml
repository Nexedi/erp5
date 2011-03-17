<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="SQL" module="Products.ZSQLMethods.SQL"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_Use_Database_Methods_Permission</string> </key>
            <value>
              <list>
                <string>Anonymous</string>
                <string>Assignee</string>
                <string>Assignor</string>
                <string>Associate</string>
                <string>Auditor</string>
                <string>Author</string>
                <string>Manager</string>
              </list>
            </value>
        </item>
        <item>
            <key> <string>allow_simple_one_argument_traversal</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>arguments_src</string> </key>
            <value> <string>base_category_uid_list\n
kw\n
search_string\n
is_full_text_search_on\n
use_text_excerpts\n
</string> </value>
        </item>
        <item>
            <key> <string>cache_time_</string> </key>
            <value> <int>0</int> </value>
        </item>
        <item>
            <key> <string>class_file_</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>class_name_</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>connection_hook</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>connection_id</string> </key>
            <value> <string>erp5_sql_connection</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>WebSite_zGetAdvancedSearchResultList</string> </value>
        </item>
        <item>
            <key> <string>max_cache_</string> </key>
            <value> <int>100</int> </value>
        </item>
        <item>
            <key> <string>max_rows_</string> </key>
            <value> <int>1000</int> </value>
        </item>
        <item>
            <key> <string>src</string> </key>
            <value> <string encoding="cdata"><![CDATA[

<dtml-comment>\n
  Use SQL method rather that catalog to speed up searching\n
</dtml-comment>\n
\n
<dtml-let query="buildSQLQuery(query=portal_catalog.getSecurityQuery(**kw), **kw)"          \n
          fix="query[\'from_table_list\'].append((\'full_text\',\'full_text\'))">\n
\n
SELECT catalog.uid, \n
       catalog.path, \n
       catalog.portal_type, \n
       catalog.title,\n
       catalog.reference, \n
       catalog.modification_date,\n
       catalog.owner,\n
       <dtml-if is_full_text_search_on> search_results.text, </dtml-if>\n
       join_category.category_uid,\n
       join_category.base_category_uid,\n
       join_category.category_relative_url,\n
       versioning.version,\n
       versioning.language\n
\n
FROM  catalog,\n
      versioning,\n
      (SELECT catalog.uid\n
              <dtml-if is_full_text_search_on>\n
                <dtml-if use_text_excerpts>\n
                /*  MySQL server can produc text excerpts */\n
                , sphinx_snippets(full_text.SearchableText, \'erp5\', \'<dtml-var "search_string">\') AS text\n
                <dtml-else>\n
                /* Return all searchable text to server which will extract found text excerpts */\n
                , full_text.SearchableText AS text\n
                </dtml-if>\n
              </dtml-if>\n
              <dtml-if "query[\'select_expression\']">\n
                ,<dtml-var "query[\'select_expression\']">\n
              </dtml-if>\n
        FROM\n
          <dtml-in prefix="table" expr="query[\'from_table_list\']">\n
            <dtml-if sequence-end>\n
                <dtml-var table_item> AS <dtml-var table_key>\n
            <dtml-else>\n
              <dtml-var table_item> AS <dtml-var table_key>,\n
            </dtml-if>\n
          </dtml-in>\n
        WHERE <dtml-var "query[\'where_expression\']"> AND  `catalog`.`uid` = `full_text`.`uid`\n
\n
        <dtml-if "query[\'order_by_expression\']"> ORDER BY <dtml-var "query[\'order_by_expression\']"> </dtml-if>\n
\n
        <dtml-if "query[\'limit_expression\']"> LIMIT <dtml-var "query[\'limit_expression\']"> \n
        <dtml-else> LIMIT 1000 </dtml-if>) \n
\n
        AS search_results LEFT JOIN \n
          (SELECT category.uid AS join_category_uid, \n
                  category.base_category_uid AS base_category_uid,\n
                  category.category_uid AS category_uid,\n
                  catalog.relative_url AS category_relative_url\n
            FROM category, catalog\n
            WHERE category.category_strict_membership = 1\n
                  AND category.base_category_uid IN \n
                    (<dtml-in prefix="loop" expr="base_category_uid_list">\n
                        <dtml-if sequence-end>\n
                          <dtml-sqlvar expr="loop_item" type="int">\n
                        <dtml-else>\n
                          <dtml-sqlvar expr="loop_item" type="int">,\n
                        </dtml-if>\n
                      </dtml-in>)\n
                  AND category.category_uid = catalog.uid\n
\n
            ) AS join_category\n
            ON search_results.uid = join_category.join_category_uid\n
\n
WHERE search_results.uid = catalog.uid AND versioning.uid = catalog.uid\n
\n
</dtml-let>

]]></string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
