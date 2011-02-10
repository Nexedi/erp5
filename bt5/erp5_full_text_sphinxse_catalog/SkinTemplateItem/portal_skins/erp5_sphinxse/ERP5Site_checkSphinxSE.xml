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
            <value> <string>portal = context.getPortalObject()\n
portal_catalog = portal.portal_catalog\n
connection = portal.erp5_sql_connection\n
sql_catalog = portal_catalog.getSQLCatalog(sql_catalog_id)\n
LIMIT = 100\n
\n
missing_uid_list = []\n
i = 0\n
while True:\n
  full_text_list = portal_catalog(SearchableText=\'!=NULL\', limit=(i*LIMIT, LIMIT))\n
  i += 1\n
  len1 = len(full_text_list)\n
  if len1 == 0:\n
    break\n
  uid_list1 = [str(x.uid) for x in full_text_list]\n
  result = connection.manage_test(\'select uid from sphinxse_index where \'\n
                                  \'sphinxse_query=\\\'filter=uid,%s;limit=%s\\\'\' % (\',\'.join(uid_list1), LIMIT))\n
  if len(result) == len1:\n
    continue\n
  uid_list2 = [str(x[0]) for x in result]\n
  missing_uid_list += [x for x in uid_list1 if x not in uid_list2]\n
if missing_uid_list:\n
  return [(x.uid, x.path) for x in portal_catalog(uid=missing_uid_list)]\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>sql_catalog_id=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_checkSphinxSE</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
