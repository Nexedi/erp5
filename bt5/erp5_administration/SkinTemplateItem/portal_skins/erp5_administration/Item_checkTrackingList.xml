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
            <value> <string>from Products.CMFActivity.ActiveResult import ActiveResult\n
portal = context.getPortalObject()\n
\n
tracking_list = list(reversed(portal.portal_simulation.getCurrentTrackingList(aggregate_uid=context.getUid())))\n
\n
for previous_brain, next_brain in zip(tracking_list, tracking_list[1:]):\n
  previous_delivery = portal.portal_catalog.getObject(previous_brain.delivery_uid)\n
  next_delivery = portal.portal_catalog.getObject(next_brain.delivery_uid)\n
  \n
  if previous_delivery.getDestination() != next_delivery.getSource():\n
    portal.restrictedTraverse(active_process).postResult(\n
     ActiveResult(summary=script.getId(),\n
         detail=\'%s has tracking error\' % context.getRelativeUrl(),\n
         result=\'\',\n
         severity=100))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>active_process, fixit=0, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Item_checkTrackingList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
