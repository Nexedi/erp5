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

def escape(data):\n
  """\n
    Escape &, <, and > in a string of data.\n
    This is a copy of the xml.sax.saxutils.escape function.\n
  """\n
  # must do ampersand first\n
  data = data.replace("&", "&amp;")\n
  data = data.replace(">", "&gt;")\n
  data = data.replace("<", "&lt;")\n
  return data\n
\n
from pprint import pformat\n
\n
ret = \'<html><body><table width=100%>\\n\'\n
\n
dict = context.showDict().items()\n
dict.sort()\n
i = 0\n
for k,v in dict:\n
  if (i % 2) == 0:\n
    c = \'#88dddd\'\n
  else:\n
    c = \'#dddd88\'\n
  i += 1\n
  ret += \'<tr bgcolor="%s"><td >%s</td><td><pre>%s</pre></td></tr>\\n\' % (escape(c), escape(k), escape(pformat(v)))\n
\n
ret += \'</table></body></html>\\n\'\n
\n
return ret\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_viewDict</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
