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
            <value> <string>""" Format the date according to current user preferences."""\n
\n
if not date:\n
  return \'\'\n
\n
try:\n
  order = context.getPortalObject().portal_preferences.getPreferredDateOrder()\n
except AttributeError:\n
  order = \'ymd\'\n
\n
y = date.year()\n
m = date.month()\n
d = date.day()\n
\n
if order == \'dmy\':\n
  result = "%02d/%02d/%04d" % (d, m, y)\n
elif order == \'mdy\':\n
  result = "%02d/%02d/%04d" % (m, d, y)\n
else: # ymd is default\n
  result = "%04d/%02d/%02d" % (y, m, d)\n
\n
if hour_minute or seconds:\n
  if seconds:\n
    hour_minute_text = "%02dh%02dmn%02ds" % (date.hour(), date.minute(), date.second())\n
  else:\n
    hour_minute_text = "%02dh%02dmn" % (date.hour(), date.minute())\n
  result = context.Base_translateString("${date} at ${hour_minute_text}", \n
              mapping = {\'date\' : result, \'hour_minute_text\' : hour_minute_text  })\n
  \n
\n
return result\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>date, hour_minute=0, seconds=0</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_FormatDate</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
