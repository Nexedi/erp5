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
            <value> <string>sale_order_list = []\n
if gid:\n
  return []\n
\n
if not id:\n
  while context_document.getParentValue().getPortalType() != "Synchronization Tool":\n
    context_document = context_document.getParentValue()\n
\n
  site = context_document.Base_getRelatedObjectList(portal_type="Integration Module")[0].getObject().getParentValue()\n
  params = {\'delivery.start_date\' : {\'query\' : site.getStartDate(), \'range\' : "min"},\n
            \'delivery.stop_date\' : {\'query\' : site.getStopDate(), \'range\' : "max"},\n
            \'default_specialise_uid\' : site.getSourceTradeUid()}\n
  sale_order_list = [x.getObject() for x in context.portal_catalog(portal_type=\'Sale Order\',\n
                                                                   simulation_state=\'confirmed\',\n
                                                                   **params)]\n
else:\n
  # work on defined sale order (id is not None)\n
  sale_order = getattr(context.sale_order_module, id)\n
  if sale_order.getSimulationState() != \'confirmed\':\n
    sale_order_list.append(sale_order)\n
\n
return sale_order_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>context_document, full=False, id="", gid=""</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>SaleOrderModule_getSaleOrderValueList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
