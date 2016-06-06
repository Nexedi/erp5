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
            <value> <string>modified = state_change[\'object\']\n
\n
grand_parent = modified.getParentValue().getParentValue()\n
\n
activate_kw=dict(after_path=modified.getPath())\n
\n
if grand_parent.getPortalType() == "Product":\n
  # If measure is local\n
  grand_parent.reindexObject(activate_kw=activate_kw)\n
else:\n
  # This was a global definition.\n
  # Its change implies that all local definitions need reindexation\n
  # Even resources that do NOT override definitions need indexation.\n
  context.activate(tag="QuantityUnitConversionDefinition_reindexResource", **activate_kw).QuantityUnitConversionModule_invalidateUniversalDefinitionDict()\n
  activate_kw["after_tag"] = "QuantityUnitConversionDefinition_reindexResource"\n
  context.product_module.recursiveReindexObject(activate_kw=activate_kw)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>QuantityUnitConversionDefinition_reindexResource</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
