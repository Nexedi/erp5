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
            <value> <string># XXX: This script is only kept in case it must be added back as a "Before" script on "_action" transition.\n
#      But it is not used any longer at the moment.\n
\n
from Products.DCWorkflow.DCWorkflow import ValidationFailed\n
from Products.ERP5Type.Message import Message\n
\n
transaction = state_change[\'object\']\n
\n
\n
date = transaction.getStartDate()\n
source = transaction.getBaobabSource(None)\n
if source is None:\n
  msg = Message(domain=\'ui\', message=\'No counter defined.\')\n
  raise ValidationFailed, (msg,)\n
\n
destination_payment = transaction.getDestinationPayment()\n
if destination_payment is None:\n
  msg = Message(domain=\'ui\', message=\'No account defined.\')\n
  raise ValidationFailed, (msg,)\n
\n
if sum([len(x.getAggregateList()) for x in transaction.objectValues(portal_type=[\'Checkbook Delivery Line\'])]) == 0:\n
  msg = Message(domain=\'ui\', message=\'No checkbook selected for delivery.\')\n
  raise ValidationFailed, (msg,)  \n
\n
at_date = transaction.getStartDate()\n
transaction.CheckbookDelivery_checkAggregateStockList(at_date=at_date, node_url = source)\n
\n
# check we are in an opened accounting day (Seb, Not required any more)\n
# transaction.Baobab_checkCounterDateOpen(site=source, date=date)\n
\n
#site = transaction.getBaobabSourceValue()\n
\n
#if \'guichet\' in site.getVaultType():\n
#  if not context.Baobab_checkCounterOpened(site):\n
#    msg = Message(domain = "ui", message="Counter is not opened")\n
#    raise ValidationFailed, (msg,)\n
\n
# Check that all checks are in draft\n
line_list = transaction.getMovementList()\n
\n
for line in line_list:\n
  aggregate_list = line.getAggregateValueList()\n
  for aggregate in aggregate_list:\n
    if aggregate.getPortalType()==\'Check\':\n
      if aggregate.getSimulationState() != \'draft\':\n
        message = Message(domain=\'ui\', message=\'Sorry, the check is not new\')\n
        raise ValidationFailed, (message,)\n
    if aggregate.getPortalType()==\'Checkbook\':\n
      if aggregate.getValidationState() != \'draft\':\n
        message = Message(domain=\'ui\', message=\'Sorry, the checkbook is not new\')\n
        raise ValidationFailed, (message,)\n
      for check in aggregate.objectValues(portal_type=\'Check\'):\n
        if check.getSimulationState() != \'draft\':\n
          message = Message(domain=\'ui\',\n
            message=\'Sorry, there is a check wich is not in the new state inside the checkbook\')\n
          raise ValidationFailed, (message,)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>checkConsistency</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
