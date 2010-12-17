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
            <value> <string>divergence_messages_list =  context.getDivergenceList()\n
\n
from Products.ERP5Type.Document import newTempBase\n
from string import zfill\n
\n
global portal_object, new_id, l\n
\n
portal_object = context.getPortalObject()\n
new_id = 0\n
l = []\n
\n
# function to create a new fast input line\n
def createInputLine(d_message):\n
  global portal_object, new_id, l\n
  new_id += 1\n
  int_len = 3\n
  \n
  o = newTempBase( portal_object\n
                 , str(new_id)\n
                 , uid =\'new_%s\' % zfill(new_id, int_len)\n
                 ,  message = str(d_message.getTranslatedMessage())\n
                 ,  tested_property_id = d_message.getProperty(\'tested_property\')\n
                 ,  object_title =  d_message.getObject().getTranslatedTitle()\n
                 ,  prevision_value = d_message.getProperty(\'prevision_value\')\n
                 ,  decision_value = d_message.getProperty(\'decision_value\')\n
                 , solver_script_list = d_message.getProperty(\'solver_script_list\'))\n
  \n
  l.append(o)\n
\n
# generate all lines for the fast input form\n
for d_message in divergence_messages_list:\n
  createInputLine(d_message)\n
  \n
# return the list of fast input lines\n
\n
return l\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Delivery_getDivergenceMessageList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
