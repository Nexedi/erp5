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
            <value> <string></string> </value>
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
            <value> <string>z_create_item</string> </value>
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
            <value> <string># Host:\n
# Database: test\n
# Table: \'item\'\n
#\n
CREATE TABLE `item` (\n
  `uid` BIGINT UNSIGNED NOT NULL,\n
  `order_id` TINYINT UNSIGNED NOT NULL,\n
  `date` datetime,\n
  `node_uid` BIGINT UNSIGNED default \'0\',\n
  `section_uid` BIGINT UNSIGNED default \'0\',\n
  `resource_uid` BIGINT UNSIGNED default \'0\',\n
  `aggregate_uid` BIGINT UNSIGNED default \'0\',\n
  `variation_text` VARCHAR(255),\n
  `simulation_state` VARCHAR(255) default \'\',\n
  PRIMARY KEY (`uid`, `aggregate_uid`,`order_id`),\n
  KEY `section_uid` (`section_uid`),\n
  KEY `resource_uid` (`resource_uid`),\n
  KEY `variation_text` (`variation_text`),\n
  KEY `aggregate_simulation_state_date` (`aggregate_uid`,`simulation_state`,`date`),\n
  KEY `node_simulation_state_date` (`node_uid`,`simulation_state`,`date`)\n
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
