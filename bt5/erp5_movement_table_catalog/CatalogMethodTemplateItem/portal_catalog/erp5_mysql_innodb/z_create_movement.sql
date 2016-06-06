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
            <value> <string>z_create_movement</string> </value>
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
# Table: \'movement\'\n
#\n
CREATE TABLE `movement` (\n
  `uid` BIGINT UNSIGNED NOT NULL,\n
  `explanation_uid` BIGINT UNSIGNED default \'0\',\n
  `source_uid` BIGINT UNSIGNED default \'0\',\n
  `destination_uid` BIGINT UNSIGNED default \'0\',\n
  `resource_uid` BIGINT UNSIGNED default \'0\',\n
  `quantity` real default \'0.0\',\n
  `start_date` datetime,\n
  `stop_date` datetime,\n
  `price` real,\n
  `is_accountable` bool,\n
  `is_divergent` bool,\n
  `variation_text` VARCHAR(255),\n
  PRIMARY KEY `uid` (`uid`),\n
  KEY `explanation_uid` (`explanation_uid`),\n
  KEY `source_uid` (`source_uid`),\n
  KEY `destination_uid` (`destination_uid`),\n
  KEY `resource_uid` (`resource_uid`),\n
  KEY `is_accountable` (`is_accountable`),\n
  KEY `variation_text` (`variation_text`)\n
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
