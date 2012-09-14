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
            <value> <string>optimised_roles_and_users</string> </value>
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
            <value> <string>z_catalog_roles_and_users_list</string> </value>
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

<dtml-let row_list="[]">\n
  <dtml-in prefix="loop" expr="_.range(_.len(optimised_roles_and_users))">\n
    <dtml-in prefix="role" expr="optimised_roles_and_users[loop_item]">\n
      <dtml-call expr="row_list.append([role_item[0], role_item[1], role_item[2]])">\n
    </dtml-in>\n
  </dtml-in>\n
  <dtml-if expr="row_list">\n
INSERT INTO\n
  roles_and_users(uid, local_roles_group_id, allowedRolesAndUsers)\n
VALUES\n
    <dtml-in prefix="row" expr="row_list">\n
(<dtml-sqlvar expr="row_item[0]" type="string">, <dtml-sqlvar expr="row_item[1]" type="string">, <dtml-sqlvar expr="row_item[2]" type="string">)\n
<dtml-if sequence-end><dtml-else>,</dtml-if>\n
    </dtml-in>\n
  </dtml-if>\n
</dtml-let>\n


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
