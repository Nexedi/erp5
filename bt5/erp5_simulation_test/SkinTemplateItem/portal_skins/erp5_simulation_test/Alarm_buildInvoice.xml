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
            <value> <string># This script is a sample of alarm script that invokes builders.\n
# You may need to modify builder ID\'s according to your application.\n
\n
portal = context.getPortalObject()\n
delivery_tool = portal.portal_deliveries\n
\n
builder_id_list = (\n
  \'purchase_invoice_builder\',\n
  \'purchase_invoice_transaction_trade_model_builder\',\n
  \'sale_invoice_builder\',\n
  \'sale_invoice_transaction_trade_model_builder\',\n
)\n
\n
for builder_id in builder_id_list:\n
  builder = getattr(delivery_tool, builder_id, None)\n
  if builder is None:\n
    continue\n
  delivery_portal_type = builder.getDeliveryPortalType()\n
  serialization_tag    = \'build:%s\' % delivery_portal_type\n
  index_tag            = \'index:%s\' % delivery_portal_type\n
  after_tag            = index_tag\n
  # depend on reindexing so that select methods\n
  # do not return movements that are already built\n
  after_method_id      = (\'recursiveImmediateReindexObject\',\n
                          \'immediateReindexObject\',\n
                          \'_updateSimulation\')\n
  activate_kw          = dict(tag=index_tag)\n
  builder.activate(\n
    limit=100,\n
    tag=\'invoice_builder_alarm\',\n
    serialization_tag=serialization_tag,\n
    after_tag=after_tag,\n
    after_method_id=after_method_id).build(activate_kw=activate_kw)\n
\n
# add a dummy activity so alarm calling can detect we still have a pending activity\n
# and do not start this script again before previous call is finished\n
context.activate(after_tag=\'invoice_builder_alarm\').getId()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Alarm_buildInvoice</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
