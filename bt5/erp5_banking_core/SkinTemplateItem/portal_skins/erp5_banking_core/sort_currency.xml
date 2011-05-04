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

def sortLine(a_Source,b_Source):\n
   if a_Source.getPortalType() in (\'Coin\', \'Banknote\'):\n
      a = a_Source\n
      b = b_Source\n
   else :\n
      a = a.getResourceValue()\n
      b = b.getResourceValue()\n
   if a.getPortalType() == b.getPortalType() :\n
      if a.getPrice() > b.getPrice() :\n
         return -1\n
      elif a.getPrice() < b.getPrice() :\n
         return 1\n
      else :\n
         if int(a.getVariation()) < int(b.getVariation()) :\n
            return 1         \n
         elif int(a.getVariation()) > int(b.getVariation()) :\n
            return -1\n
         else :\n
            return 0\n
   elif a.getPortalType() == \'Banknote\':\n
      return -1\n
   else:\n
      return 1\n
\n
\n
listCurrency.sort(sortLine)\n
return listCurrency\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>listCurrency,</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>sort_currency</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
