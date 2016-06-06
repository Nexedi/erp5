<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <tuple>
        <global name="SQL" module="Products.ZSQLMethods.SQL"/>
        <tuple/>
      </tuple>
    </pickle>
    <pickle>
      <dictionary>
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
                                <key> <string>id_account</string> </key>
                                <value>
                                  <dictionary>
                                    <item>
                                        <key> <string>default</string> </key>
                                        <value> <string></string> </value>
                                    </item>
                                  </dictionary>
                                </value>
                            </item>
                            <item>
                                <key> <string>id_accounting</string> </key>
                                <value>
                                  <dictionary>
                                    <item>
                                        <key> <string>default</string> </key>
                                        <value> <string></string> </value>
                                    </item>
                                  </dictionary>
                                </value>
                            </item>
                          </dictionary>
                        </value>
                    </item>
                    <item>
                        <key> <string>_keys</string> </key>
                        <value>
                          <list>
                            <string>id_accounting</string>
                            <string>id_account</string>
                          </list>
                        </value>
                    </item>
                  </dictionary>
                </state>
              </object>
            </value>
        </item>
        <item>
            <key> <string>_col</string> </key>
            <value>
              <list>
                <dictionary>
                  <item>
                      <key> <string>name</string> </key>
                      <value> <string>source_accounting</string> </value>
                  </item>
                  <item>
                      <key> <string>null</string> </key>
                      <value> <int>1</int> </value>
                  </item>
                  <item>
                      <key> <string>type</string> </key>
                      <value> <string>t</string> </value>
                  </item>
                  <item>
                      <key> <string>width</string> </key>
                      <value> <int>15</int> </value>
                  </item>
                </dictionary>
                <dictionary>
                  <item>
                      <key> <string>name</string> </key>
                      <value> <string>destination_accounting</string> </value>
                  </item>
                  <item>
                      <key> <string>null</string> </key>
                      <value> <int>1</int> </value>
                  </item>
                  <item>
                      <key> <string>type</string> </key>
                      <value> <string>t</string> </value>
                  </item>
                  <item>
                      <key> <string>width</string> </key>
                      <value> <int>15</int> </value>
                  </item>
                </dictionary>
                <dictionary>
                  <item>
                      <key> <string>name</string> </key>
                      <value> <string>resource</string> </value>
                  </item>
                  <item>
                      <key> <string>null</string> </key>
                      <value> <int>0</int> </value>
                  </item>
                  <item>
                      <key> <string>type</string> </key>
                      <value> <string>t</string> </value>
                  </item>
                  <item>
                      <key> <string>width</string> </key>
                      <value> <int>13</int> </value>
                  </item>
                </dictionary>
                <dictionary>
                  <item>
                      <key> <string>name</string> </key>
                      <value> <string>quantity</string> </value>
                  </item>
                  <item>
                      <key> <string>null</string> </key>
                      <value> <int>1</int> </value>
                  </item>
                  <item>
                      <key> <string>type</string> </key>
                      <value> <string>n</string> </value>
                  </item>
                  <item>
                      <key> <string>width</string> </key>
                      <value> <int>18</int> </value>
                  </item>
                </dictionary>
                <dictionary>
                  <item>
                      <key> <string>name</string> </key>
                      <value> <string>path</string> </value>
                  </item>
                  <item>
                      <key> <string>null</string> </key>
                      <value> <int>1</int> </value>
                  </item>
                  <item>
                      <key> <string>type</string> </key>
                      <value> <string>t</string> </value>
                  </item>
                  <item>
                      <key> <string>width</string> </key>
                      <value> <int>73</int> </value>
                  </item>
                </dictionary>
                <dictionary>
                  <item>
                      <key> <string>name</string> </key>
                      <value> <string>reference</string> </value>
                  </item>
                  <item>
                      <key> <string>null</string> </key>
                      <value> <int>1</int> </value>
                  </item>
                  <item>
                      <key> <string>type</string> </key>
                      <value> <string>t</string> </value>
                  </item>
                  <item>
                      <key> <string>width</string> </key>
                      <value> <int>29</int> </value>
                  </item>
                </dictionary>
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
            <value> <string>id_accounting=""\r\n
id_account=""</string> </value>
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
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>connection_id</string> </key>
            <value> <string>accounting_sql_connection</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>accounting_line</string> </value>
        </item>
        <item>
            <key> <string>max_cache_</string> </key>
            <value> <int>100</int> </value>
        </item>
        <item>
            <key> <string>max_rows_</string> </key>
            <value> <int>1000000</int> </value>
        </item>
        <item>
            <key> <string>src</string> </key>
            <value> <string encoding="cdata"><![CDATA[

SELECT\n
  IF (journal_code in (\'PI\', \'PC\'), \'\', CONCAT(\'Account \', account_code)) AS source_accounting,\n
  IF (journal_code in (\'PI\', \'PC\'), CONCAT(\'Account \', account_code), \'\') AS destination_accounting,\n
  \'Currency Euro\' AS resource,\n
  IF (journal_code in (\'PI\', \'PC\'), debit - credit, credit - debit) AS quantity,\n
  CONCAT(\'<dtml-var getPath>/accounting_module/\', transaction_reference, \' \', journal_code, \' \', date) AS path,\n
  CONCAT(\'Accounting \', transaction_reference, \' \', journal_code, \' \', date) AS reference\n
FROM\n
  NOMACTX\n
<dtml-if expr="id_accounting or id_account">\n
WHERE\n
  <dtml-if expr="id_accounting">\n
    CONCAT(transaction_reference, \' \', journal_code, \' \', date) = <dtml-sqlvar type="string" expr="id_accounting">\n
  </dtml-if>\n
  <dtml-if expr="id_accounting and id_account">\n
    AND\n
  </dtml-if>\n
  <dtml-if expr="id_account">\n
    account_code = <dtml-sqlvar type="string" expr="id_account">\n
  </dtml-if>\n
</dtml-if>\n
ORDER BY\n
  transaction_reference ASC,\n
  journal_code ASC,\n
  date ASC\n


]]></string> </value>
        </item>
        <item>
            <key> <string>template</string> </key>
            <value>
              <object>
                <klass>
                  <global name="__newobj__" module="copy_reg"/>
                </klass>
                <tuple>
                  <global name="SQL" module="Shared.DC.ZRDB.DA"/>
                </tuple>
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

SELECT\n
  IF (journal_code in (\'PI\', \'PC\'), \'\', CONCAT(\'Account \', account_code)) AS source_accounting,\n
  IF (journal_code in (\'PI\', \'PC\'), CONCAT(\'Account \', account_code), \'\') AS destination_accounting,\n
  \'Currency Euro\' AS resource,\n
  IF (journal_code in (\'PI\', \'PC\'), debit - credit, credit - debit) AS quantity,\n
  CONCAT(\'<dtml-var getPath>/accounting_module/\', transaction_reference, \' \', journal_code, \' \', date) AS path,\n
  CONCAT(\'Accounting \', transaction_reference, \' \', journal_code, \' \', date) AS reference\n
FROM\n
  NOMACTX\n
<dtml-if expr="id_accounting or id_account">\n
WHERE\n
  <dtml-if expr="id_accounting">\n
    CONCAT(transaction_reference, \' \', journal_code, \' \', date) = <dtml-sqlvar type="string" expr="id_accounting">\n
  </dtml-if>\n
  <dtml-if expr="id_accounting and id_account">\n
    AND\n
  </dtml-if>\n
  <dtml-if expr="id_account">\n
    account_code = <dtml-sqlvar type="string" expr="id_account">\n
  </dtml-if>\n
</dtml-if>\n
ORDER BY\n
  transaction_reference ASC,\n
  journal_code ASC,\n
  date ASC\n


]]></string> </value>
                    </item>
                  </dictionary>
                </state>
              </object>
            </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Accounting</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
