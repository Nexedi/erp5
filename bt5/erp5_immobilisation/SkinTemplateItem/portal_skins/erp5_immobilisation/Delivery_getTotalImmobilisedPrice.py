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
            <value> <string># Returns the total price declared as immobilised for all aggregated items\n
from DateTime import DateTime\n
\n
millis = DateTime(\'2000/01/01 12:00:00.001\') - DateTime(\'2000/01/01 12:00:00\')\n
\n
self = context\n
stop_date = self.getStopDate() + millis\n
if stop_date is None:\n
  return None\n
item_list = []\n
for line in self.contentValues():\n
  try:\n
    item_list += line.getAggregateValueList()\n
  except:\n
    pass\n
price = 0\n
for item in item_list:\n
  try:\n
    price += item.getLastImmobilisationInitialPrice(at_date=stop_date, **kw)\n
  except:\n
    pass\n
return price\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Delivery_getTotalImmobilisedPrice</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
