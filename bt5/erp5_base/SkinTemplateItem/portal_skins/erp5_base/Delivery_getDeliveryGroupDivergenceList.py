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
            <value> <string>from Products.ERP5Type.Document import newTempBase\n
\n
divergence_list =  context.getDivergenceList()\n
portal_object = context.getPortalObject()\n
l = []\n
\n
candidate_dict = {}\n
\n
for divergence in divergence_list:\n
  prop = divergence.getProperty(\'tested_property\')\n
  if prop in (None, \'\') or divergence.getCollectOrderGroup() != \'delivery\':\n
    continue\n
  message, candidate_list, value_list, decision_title_list, prevision_title_list = candidate_dict.get(prop, [\'\', [], [], [], []])\n
  decision_value = divergence.getProperty(\'decision_value\')\n
  decision_title = divergence.getProperty(\'decision_title\', decision_value)\n
  prevision_value = divergence.getProperty(\'prevision_value\')\n
  prevision_title = divergence.getProperty(\'prevision_title\', prevision_value)\n
  object_relative_url = divergence.getProperty(\'object_relative_url\')\n
  simulation_movement_url = divergence.getProperty(\'simulation_movement\').getRelativeUrl()\n
  object = portal_object.restrictedTraverse(object_relative_url)\n
  if decision_value not in value_list:\n
    candidate_list.append((decision_title, object_relative_url))\n
    value_list.append(decision_value)\n
  if decision_title not in decision_title_list:\n
    decision_title_list.append(decision_title)\n
  if prevision_value not in value_list:\n
    candidate_list.append((prevision_title, simulation_movement_url))\n
    value_list.append(prevision_value)\n
  if prevision_title not in prevision_title_list:\n
    prevision_title_list.append(prevision_title)\n
  candidate_dict[prop] = [divergence.getTranslatedMessage(), candidate_list, value_list, decision_title_list, prevision_title_list]\n
\n
for prop, candidate_list in candidate_dict.items():\n
  uid = \'new_%s\' % prop\n
  object = context\n
\n
  o = newTempBase(context.getParentValue(), context.getId(), uid, uid=uid,\n
                  message=candidate_list[0],\n
                  object_title=object.getTranslatedTitle(),\n
                  decision_title=\', \'.join([str(x) for x in candidate_list[3]]),\n
                  prevision_title=\', \'.join([str(x) for x in candidate_list[4]]),\n
                  candidate_list=[(context.Base_translateString(\'Do nothing\'), \'ignore\')]+candidate_list[1])\n
  l.append(o)\n
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
            <value> <string>Delivery_getDeliveryGroupDivergenceList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
