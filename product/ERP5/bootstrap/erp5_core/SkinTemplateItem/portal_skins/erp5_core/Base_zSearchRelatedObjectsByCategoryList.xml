<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="SQL" module="Products.ZSQLMethods.SQL"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>allow_simple_one_argument_traversal</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>arguments_src</string> </key>
            <value> <string>category_list\r\n
portal_type\r\n
strict_membership\r\n
where_expression\r\n
order_by_expression</string> </value>
        </item>
        <item>
            <key> <string>cache_time_</string> </key>
            <value> <int>0</int> </value>
        </item>
        <item>
            <key> <string>class_file_</string> </key>
            <value> <string>ZSQLCatalog.zsqlbrain</string> </value>
        </item>
        <item>
            <key> <string>class_name_</string> </key>
            <value> <string>ZSQLBrain</string> </value>
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
            <value> <string>Base_zSearchRelatedObjectsByCategoryList</string> </value>
        </item>
        <item>
            <key> <string>max_cache_</string> </key>
            <value> <int>100</int> </value>
        </item>
        <item>
            <key> <string>max_rows_</string> </key>
            <value> <int>0</int> </value>
        </item>
        <item>
            <key> <string>src</string> </key>
            <value> <string encoding="cdata"><![CDATA[

SELECT DISTINCT catalog.uid, path, relative_url, portal_type\n
FROM catalog, category\n
WHERE catalog.uid = category.uid\n
  <dtml-if portal_type>\n
    AND <dtml-sqltest portal_type type="string" multiple>\n
  </dtml-if>\n
  AND (<dtml-var "portal_categories.buildSQLSelector(category_list)">)\n
  <dtml-if strict_membership>\n
    AND category.category_strict_membership = 1\n
  </dtml-if>\n
  <dtml-if where_expression>\n
    AND <dtml-var where_expression>\n
  </dtml-if>\n
<dtml-if order_by_expression>\n
ORDER BY\n
  <dtml-var order_by_expression>\n
</dtml-if>

]]></string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Search Category</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
