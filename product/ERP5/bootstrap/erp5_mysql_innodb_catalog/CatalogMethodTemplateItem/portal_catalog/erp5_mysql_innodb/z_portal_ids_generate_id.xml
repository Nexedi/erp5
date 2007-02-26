<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <tuple>
        <tuple>
          <string>Products.ZSQLMethods.SQL</string>
          <string>SQL</string>
        </tuple>
        <none/>
      </tuple>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>__ac_local_roles__</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>_arg</string> </key>
            <value>
              <object>
                <klass>
                  <global name="Args" module="Shared.DC.ZRDB.Aqueduct"/>
                </klass>
                <tuple/>
                <state>
                  <dictionary>
                    <item>
                        <key> <string>_data</string> </key>
                        <value>
                          <dictionary>
                            <item>
                                <key> <string>default</string> </key>
                                <value>
                                  <dictionary>
                                    <item>
                                        <key> <string>type</string> </key>
                                        <value> <string>int</string> </value>
                                    </item>
                                  </dictionary>
                                </value>
                            </item>
                            <item>
                                <key> <string>id_group</string> </key>
                                <value>
                                  <dictionary/>
                                </value>
                            </item>
                          </dictionary>
                        </value>
                    </item>
                    <item>
                        <key> <string>_keys</string> </key>
                        <value>
                          <list>
                            <string>id_group</string>
                            <string>default</string>
                          </list>
                        </value>
                    </item>
                  </dictionary>
                </state>
              </object>
            </value>
        </item>
        <item>
            <key> <string>arguments_src</string> </key>
            <value> <string>id_group\r\n
default:int</string> </value>
        </item>
        <item>
            <key> <string>connection_id</string> </key>
            <value> <string>erp5_sql_transactionless_connection</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>z_portal_ids_generate_id</string> </value>
        </item>
        <item>
            <key> <string>src</string> </key>
            <value> <string encoding="cdata"><![CDATA[

# DO NOT FORGET TO COMMIT AFTER !!\n
# commit ZSQL method should be z_portal_ids_commit\n
\n
BEGIN\n
<dtml-var sql_delimiter>\n
INSERT INTO portal_ids (`id_group`, `last_id`) VALUES (<dtml-sqlvar id_group type="string">, LAST_INSERT_ID(<dtml-sqlvar default type="int">)) ON DUPLICATE KEY UPDATE `last_id` = LAST_INSERT_ID(`last_id` + 1)\n
<dtml-var sql_delimiter>\n
SELECT LAST_INSERT_ID()

]]></string> </value>
        </item>
        <item>
            <key> <string>template</string> </key>
            <value>
              <object>
                <klass>
                  <global name="SQL" module="Shared.DC.ZRDB.DA"/>
                </klass>
                <none/>
                <state>
                  <dictionary>
                    <item>
                        <key> <string>__name__</string> </key>
                        <value> <string encoding="cdata"><![CDATA[

<string>

]]></string> </value>
                    </item>
                    <item>
                        <key> <string>_vars</string> </key>
                        <value>
                          <dictionary/>
                        </value>
                    </item>
                    <item>
                        <key> <string>globals</string> </key>
                        <value>
                          <dictionary/>
                        </value>
                    </item>
                    <item>
                        <key> <string>raw</string> </key>
                        <value> <string encoding="cdata"><![CDATA[

# DO NOT FORGET TO COMMIT AFTER !!\n
# commit ZSQL method should be z_portal_ids_commit\n
\n
BEGIN\n
<dtml-var sql_delimiter>\n
INSERT INTO portal_ids (`id_group`, `last_id`) VALUES (<dtml-sqlvar id_group type="string">, LAST_INSERT_ID(<dtml-sqlvar default type="int">)) ON DUPLICATE KEY UPDATE `last_id` = LAST_INSERT_ID(`last_id` + 1)\n
<dtml-var sql_delimiter>\n
SELECT LAST_INSERT_ID()

]]></string> </value>
                    </item>
                  </dictionary>
                </state>
              </object>
            </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
