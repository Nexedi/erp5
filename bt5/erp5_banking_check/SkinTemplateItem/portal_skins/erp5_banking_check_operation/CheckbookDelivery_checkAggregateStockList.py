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
            <value> <string>from Products.DCWorkflow.DCWorkflow import ValidationFailed\n
from Products.ERP5Type.Message import Message\n
\n
aggregate_uid_list = [x.uid for x in context.portal_simulation.getCurrentTrackingList(\n
                         at_date=at_date, node=node_url,\n
                         where_expression="item_catalog.portal_type IN (\'Check\', \'Checkbook\')")]\n
for line in context.getMovementList():\n
  for aggregate_value in line.getAggregateValueList():\n
    if aggregate_value.getUid() not in aggregate_uid_list:\n
      reference = aggregate_value.getReference()\n
      if reference is None:\n
        reference = \'%s - %s\' % (aggregate_value.getReferenceRangeMin() or \'\', aggregate_value.getReferenceRangeMax() or \'\')\n
      msg = Message(domain="ui", message="Sorry, the item with reference $reference is not available any more",\n
                    mapping={\'reference\':reference})\n
      raise ValidationFailed, (msg,)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>node_url=None, at_date=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>CheckbookDelivery_checkAggregateStockList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
