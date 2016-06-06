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
            <value> <string encoding="cdata"><![CDATA[

from Products.ERP5Type.Document import newTempBase\n
from Products.ZSQLCatalog.SQLCatalog import ComplexQuery, SimpleQuery\n
from DateTime import DateTime\n
\n
rev_query_list = []\n
if isinstance(kw.get(\'from_date\'), DateTime):\n
  rev_query_list.append(SimpleQuery(creation_date=kw[\'from_date\'],\n
                                    comparison_operator=\'>=\'))\n
if isinstance(kw.get(\'at_date\'), DateTime):\n
  rev_query_list.append(SimpleQuery(creation_date=kw[\'at_date\'],\n
                                    comparison_operator=\'<=\'))\n
\n
test_result_list = []\n
revision = None\n
new_test_result_list = []\n
context.log("rev_query_list", rev_query_list)\n
if rev_query_list:\n
  result = context.searchFolder(title=\'PERF-ERP5-MASTER\', simulation_state=\'stopped\',\n
    revision=ComplexQuery(operator=\'AND\', *rev_query_list),\n
    sort_on=((\'delivery.start_date\', \'ASC\'),),src__=1)\n
  context.log("result", result)\n
  for test in context.searchFolder(title=\'PERF-ERP5-MASTER\', simulation_state=\'stopped\',\n
    revision=ComplexQuery(operator=\'AND\', *rev_query_list),\n
    sort_on=((\'delivery.start_date\', \'ASC\'),)):\n
    test = test.getObject()\n
    if revision != test.getReference():\n
      revision = test.getReference()\n
      test_result = {\'rev\': str(revision)}\n
      test_result_list.append(test_result)\n
    for prop in \'all_tests\', \'failures\', \'errors\':\n
      test_result[prop] = test_result.get(prop, 0) + test.getProperty(prop, 0)\n
    line_list = test.TestResult_getTestPerfTimingList()\n
    timing_dict = test_result.setdefault(\'timing_dict\', {})\n
    for line in line_list:\n
      for k, v in line.items():\n
        timing_dict.setdefault(k, []).append(v)\n
\n
  normalize = kw.get(\'normalize\')\n
  base_result = {}\n
\n
  for test_result in test_result_list:\n
    if test_result[\'errors\'] < test_result[\'all_tests\']:\n
      new_test_result = newTempBase(context, \'\')\n
      for k, v in test_result.pop(\'timing_dict\').items():\n
        if v:\n
          v = sum(v) / len(v)\n
          test_result[k] = v / base_result.setdefault(k, normalize and v or 1)\n
      new_test_result.edit(**test_result)\n
      new_test_result_list.append(new_test_result)\n
\n
return new_test_result_list\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>*args, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>TestResultModule_getTestPerfResultList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
