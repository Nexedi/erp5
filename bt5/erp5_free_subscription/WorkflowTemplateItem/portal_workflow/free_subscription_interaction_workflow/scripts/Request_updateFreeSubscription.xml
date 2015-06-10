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
            <value> <string>request = state_change["object"]\n
\n
if request.getFreeSubscriptionRequestType() == "unsubscription":\n
  free_subscription = request.getFollowUpValue()\n
  if free_subscription.getValidationState() != "invalidated":\n
    free_subscription.invalidate()\n
elif request.getFreeSubscriptionRequestType() == "subscription":\n
  from DateTime import DateTime\n
  portal = request.getPortalObject()\n
  free_subscription = portal.free_subscription_module.newContent(\n
    source=request.getSource(),\n
    destination=request.getDestination(),\n
    resource=request.getResource(),\n
    effective_date=DateTime())\n
  free_subscription.validate()\n
  request.setFollowUpValue(free_subscription)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Request_updateFreeSubscription</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
