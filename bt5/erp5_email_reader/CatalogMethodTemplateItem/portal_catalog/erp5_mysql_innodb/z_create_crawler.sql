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
            <value> <string>z_create_crawler</string> </value>
        </item>
        <item>
            <key> <string>src</string> </key>
            <value> <string>CREATE TABLE `crawler` (\n
  `uid` BIGINT UNSIGNED NOT NULL,\n
  `frequency_index` INT,\n
  `creation_date_index` INT,\n
  PRIMARY KEY  (`uid`),\n
  KEY `creation_date_index` (`creation_date_index`, `frequency_index`)\n
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
