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
            <value> <string>"""\n
  Find the list of objects to synchronize by calling the catalog.\n
\n
  Possibly look up a single object based on its ID, GID\n
"""\n
\n
payment_transaction_list = []\n
payment_transaction_append = payment_transaction_list.append\n
\n
if gid:\n
  return []\n
\n
if full:\n
  return context.getPortalObject().organisation_module.contentValues()\n
\n
if not id:\n
  # first get the related integration site\n
  while context_document.getParentValue().getPortalType() != "Synchronization Tool":\n
    context_document = context_document.getParentValue()\n
  site = [x for x in context_document.Base_getRelatedObjectList(portal_type="Integration Module")][0].getParentValue()\n
  context.log("site %s" % site)\n
\n
  # then browse list of stc related to the site one\n
  default_stc = site.getSourceTradeValue()\n
  for document in default_stc.Base_getRelatedObjectList(portal_type="Sale Trade Condition",\n
                                                        validation_state="validated"):\n
    for payment_transaction in document.Base_getRelatedObjectList(portal_type="Payment Transaction",\n
                                                        simulation_state="confirmed"):\n
      transaction = payment_transaction.getObject()\n
      payment_transaction_append(transaction)\n
else:\n
  # work on defined payment transaction (id is not None)\n
  payment_transaction = getattr(context.accounting_module, id)\n
  if payment_transaction.getSimulationState() != \'confirmed\':\n
    payment_transaction_append(payment_transaction)\n
\n
return payment_transaction_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>context_document, full=False, id="", gid=""</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>PaymentTransactionModule_getPaymentTransactionValueList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
