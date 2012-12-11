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
            <value> <string>for builder in sorted(context.getPortalObject().portal_orders.contentValues(),\n
                  key=lambda x:x.getTitle()):\n
  print builder.getId()\n
  print "  Title: %s" % (builder.getTitle())\n
  print "  Simulation Select Method: %s" % (builder.getSimulationSelectMethodId())\n
  print "  Delivery Select Method: %s" % (builder.getDeliverySelectMethodId())\n
  print "  After Generation Script: %s" % (builder.getDeliveryAfterGenerationScriptId())\n
  print "  Delivery Module Before Building Script: %s" % (builder.getDeliveryModuleBeforeBuildingScriptId())\n
  print\n
\n
  for mg in sorted(builder.contentValues(), key=lambda x:x.getTitle()):\n
    print builder.getId()\n
    print " ", "\\n  ".join([x for x in (\n
      "Id: %s" % mg.getId(),\n
      "Title: %s" % mg.getTitle(),\n
      "Type: %s" % mg.getPortalType(),\n
      "Collect Order Group: %s" % mg.getCollectOrderGroup(),\n
      "Tested Properties: %r" % mg.getTestedPropertyList(),\n
      "Update Always: %r" % mg.isUpdateAlways(),\n
\n
      )])\n
    print\n
\n
return printed\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_dumpOrderBuilderList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
