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

from Products.ERP5Type.Document import newTempBase\n
\n
divergence_list =  context.getDivergenceList()\n
portal_object = context.getPortalObject()\n
l = []\n
\n
for divergence in divergence_list:\n
  if divergence.getCollectOrderGroup() != \'cell\':\n
    continue\n
  decision_value = divergence.getProperty(\'decision_value\')\n
  decision_title = divergence.getProperty(\'decision_title\', decision_value)\n
  prevision_value = divergence.getProperty(\'prevision_value\')\n
  prevision_title = divergence.getProperty(\'prevision_title\', prevision_value)\n
  object_relative_url = divergence.getProperty(\'object_relative_url\')\n
  simulation_movement_url = divergence.getProperty(\'simulation_movement\').getRelativeUrl()\n
  uid = \'new_%s&%s\' % (simulation_movement_url,\n
                       divergence.getProperty(\'tested_property\'))\n
\n
  object = portal_object.restrictedTraverse(object_relative_url)\n
  o = newTempBase(object.getParentValue(), object.getId(), uid=uid,\n
                  message=str(divergence.getTranslatedMessage()),\n
                  object_title=object.getTranslatedTitle(),\n
                  prevision_title=prevision_title,\n
                  decision_title=decision_title,\n
                  candidate_list=[(context.Base_translateString(\'Do nothing\'), \'ignore\'),\n
                                  (decision_title, \'accept\'),\n
                                  (prevision_title, \'adopt\'),])\n
  l.append(o)\n
\n
return l\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Delivery_getCellGroupDivergenceList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
