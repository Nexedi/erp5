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
            <value> <string>"""Return the \'side-specific\' reference, ie. the source reference or\n
destination reference.\n
"""\n
delivery = brain.getObject().getExplanationValue()\n
if brain.section_uid != brain.mirror_section_uid:\n
  if delivery.getSourceSectionUid() == brain.section_uid:\n
    return delivery.getSourceReference()\n
  return delivery.getDestinationReference()\n
\n
# If we have a movement which exists for both section uid and mirror section uid,\n
# we can only guess what reference should be used.\n
if round(brain.total_quantity - brain.getObject().getQuantity(), 5) == 0:\n
  return delivery.getDestinationReference()\n
\n
return delivery.getSourceReference()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>brain, selection=None, **kwd</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Movement_getSpecificReference</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
