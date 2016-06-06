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

if not date:\n
  return \'\'\n
try:\n
  now =  DateTime()\n
  date = DateTime(date)\n
except:\n
  return \'\'  \n
Base_translateString = context.Base_translateString\n
diff = now - date\n
if diff < 1:\n
  hours = diff*24.0\n
  if hours < 1:\n
    minutes = hours*60.0\n
    if minutes < 1:\n
      seconds = minutes*60.0\n
      if seconds < 1:\n
        return Base_translateString(\'Now\')\n
      if 2 > seconds > 1: \n
        return Base_translateString(\'${timedif} second ago\', mapping={\'timedif\':int(seconds)})\n
      return Base_translateString(\'${timedif} seconds ago\', mapping={\'timedif\':int(seconds)})\n
    if 2 > minutes > 1:\n
      return Base_translateString(\'${timedif} minute ago\', mapping={\'timedif\':int(minutes)})\n
    return Base_translateString(\'${timedif} minutes ago\', mapping={\'timedif\':int(minutes)})\n
  if 2 > hours > 1:\n
    return Base_translateString(\'${timedif} hour ago\', mapping={\'timedif\':int(hours)})\n
  return Base_translateString(\'${timedif} hours ago\', mapping={\'timedif\':int(hours)})\n
else:\n
  if diff > 365.25:\n
    return Base_translateString(\'More than 1 year\')\n
  elif diff > 30:\n
    return Base_translateString(\'More than 1 month\')\n
  elif 2 > diff > 1:\n
    return Base_translateString(\'Yesterday\')\n
  return Base_translateString(\'${timedif} days ago\', mapping={\'timedif\':int(diff)})\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>date</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getDiffBetweenDateAndNow</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Return diff between the date pass in parameter and current date</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
