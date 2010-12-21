<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="PythonScript" module="Products.PythonScripts.PythonScript"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>Script_magic</string> </key>
            <value> <int>3</int> </value>
        </item>
        <item>
            <key> <string>_bind_names</string> </key>
            <value>
              <object>
                <klass>
                  <global name="NameAssignments" module="Shared.DC.Scripts.Bindings"/>
                </klass>
                <tuple/>
                <state>
                  <dictionary>
                    <item>
                        <key> <string>_asgns</string> </key>
                        <value>
                          <dictionary>
                            <item>
                                <key> <string>name_container</string> </key>
                                <value> <string>container</string> </value>
                            </item>
                            <item>
                                <key> <string>name_context</string> </key>
                                <value> <string>context</string> </value>
                            </item>
                            <item>
                                <key> <string>name_m_self</string> </key>
                                <value> <string>script</string> </value>
                            </item>
                            <item>
                                <key> <string>name_subpath</string> </key>
                                <value> <string>traverse_subpath</string> </value>
                            </item>
                          </dictionary>
                        </value>
                    </item>
                  </dictionary>
                </state>
              </object>
            </value>
        </item>
        <item>
            <key> <string>_body</string> </key>
            <value> <string>params = context.portal_selections.getSelectionParamsFor(selection_name)\n
\n
params[\'stat\'] = 1\n
params[\'omit_input\'] = 1\n
params[\'omit_output\'] = 0\n
\n
if (params.get(\'operation_date\') or {}).get(\'query\'):\n
  buildSQLQuery = context.portal_catalog.buildSQLQuery\n
  params[\'source_section_where_expression\'] = buildSQLQuery(\n
            **{\'delivery.start_date\': params[\'operation_date\']})[\'where_expression\']\n
  params[\'destination_section_where_expression\'] = buildSQLQuery(\n
            **{\'delivery.stop_date\': params[\'operation_date\']})[\'where_expression\']\n
  del params[\'operation_date\']\n
\n
result = context.AccountingTransactionModule_zGetAccountingTransactionList(\n
              selection=selection,\n
              selection_params=params, **params)\n
row = result[0]\n
return float(\'%.02f\' % (row.total_price and - row.total_price or 0.0))\n
# vim: syntax=python\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>selection=None, selection_name=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>AccountingTransactionModule_statSourceCredit</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
