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

""" display value in the cell according to (french) fiscality rules """\n
context.log(cell_name, cell_value)\n
\n
if same_type(cell_value, 0) or same_type(cell_value, 0.0) : \n
  number = cell_value\n
  if number == 0 : \n
    return ""\n
\n
  negative = number < 0\n
  amount = str(abs(number))\n
  indexes = range(len(amount))\n
  indexes.reverse()\n
  string = \'\'\n
  count = 0\n
  for i in indexes :\n
    if not count % 3 :\n
      string = \' \' + string\n
    string = amount[i] + string\n
    count += 1\n
  if negative :\n
    string = "(%s)"%string.strip()\n
  return string\n
else :\n
  return cell_value\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>cell_value, cell_name</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>FiscalReportCell_formatCell</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
