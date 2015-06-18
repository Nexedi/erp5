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
            <value> <string>#from decimal import Decimal\n
import datetime\n
import json\n
from DateTime import DateTime\n
\n
response = container.REQUEST.RESPONSE\n
\n
try:\n
  results = context.manage_test(query)\n
  data = [ results.names() ]\n
  data.extend(results.tuples())\n
except Exception, e:\n
  response.setStatus(500)\n
  try:\n
    response.write(str(e[1]))\n
  except Exception:\n
    response.write(str(e))\n
  return\n
\n
# handle non JSON serializable data\n
new_data = [data[0]]\n
for line in data[1:]:\n
  new_line = []\n
  for v in line:\n
    if isinstance(v, DateTime):\n
      v = v.ISO()\n
    elif isinstance(v, datetime.datetime):\n
      v = v.isoformat()\n
    elif "Decimal" in repr(v): # XXX decimal is not allowed in restricted environment\n
      v = float(v)\n
    new_line.append(v)\n
  new_data.append(new_line)\n
\n
response.setHeader(\'Content-Type\', \'application/json\')\n
return json.dumps(new_data, indent=2)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>query=""</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ZMySQLDAConnection_getQueryResultAsJSON</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
