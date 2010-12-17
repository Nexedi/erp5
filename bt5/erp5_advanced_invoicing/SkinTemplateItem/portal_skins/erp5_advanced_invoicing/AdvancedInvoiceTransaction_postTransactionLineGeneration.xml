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
            <value> <string>#\n
#  this script is called on the Invoice Transaction\n
# after the advanced_invoice_transaction_builder created accounting lines in the invoice\n
# \n
\n
# copy title\n
invoice_transaction = context \n
related_invoice = invoice_transaction.getDefaultCausalityValue()\n
if not invoice_transaction.hasTitle() and related_invoice is not None and related_invoice.hasTitle():\n
  invoice_transaction.setTitle(related_invoice.getTitle())\n
\n
context.InvoiceTransaction_postTransactionLineGeneration(**kw)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>related_simulation_movement_path_list=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>AdvancedInvoiceTransaction_postTransactionLineGeneration</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
