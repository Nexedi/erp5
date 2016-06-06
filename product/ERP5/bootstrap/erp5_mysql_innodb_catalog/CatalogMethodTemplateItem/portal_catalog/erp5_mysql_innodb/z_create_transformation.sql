<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="SQL" module="Products.ZSQLMethods.SQL"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_col</string> </key>
            <value>
              <tuple/>
            </value>
        </item>
        <item>
            <key> <string>arguments_src</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>connection_id</string> </key>
            <value> <string>erp5_sql_connection</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>z_create_transformation</string> </value>
        </item>
        <item>
            <key> <string>src</string> </key>
            <value> <string>CREATE TABLE `transformation` (\n
  `uid` bigint(20) unsigned NOT NULL,\n
  `variation_text` varchar(255) default \'\',\n
  `transformed_uid` bigint(20) unsigned NOT NULL,\n
  `transformed_variation_text` varchar(255) default \'\',\n
  `quantity` double,\n
  KEY `resource` (`uid`, `variation_text`),\n
  KEY `transformed_resource` (`transformed_uid`, `transformed_variation_text`)\n
) ENGINE=InnoDB;\n
</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
