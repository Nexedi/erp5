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

print \'<html><head><meta http-equiv="refresh" content="%s"></head><body>\' % refresh_interval\n
\n
for table in \'message\', \'message_queue\':\n
  q = """SELECT count(*) AS %(table)s, method_id, processing, processing_node AS node, min(priority) AS min_pri, max(priority) AS max_pri\n
           FROM %(table)s GROUP BY method_id, processing, processing_node ORDER BY node""" % dict(table=table)\n
\n
  print "<table border=\\"\\" style=\\"font-size:XX-small;\\"><tbody> <tr><th>%s</th> <th>method_id</th> <th>processing</th> <th>node</th> <th>min_pri</th> <th>max_pri</th> </tr>" % table\n
  for row in context.cmf_activity_sql_connection.manage_test(q):\n
    print \'<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td</tr>\' % (row[table], row[\'method_id\'], row[\'processing\'], row[\'node\'], row[\'min_pri\'], row[\'max_pri\'])\n
  print \'</tbody> </table> <br/>\'\n
\n
return printed\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>refresh_interval=5</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ActivityTool_watchActivities</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
