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
# after the invoice_transaction_builder delivery builder\n
# created accounting lines in the invoice\n
# \n
\n
# Accounting specific: \n
#  if every lines have the same resource, then copy the resource \n
# on the Transaction and delete resource on the lines.\n
# TODO: this is a Property Assignment Movement Group\n
\n
line_list = context.objectValues(\n
  portal_type=context.getPortalAccountingMovementTypeList())\n
resource_set = set(line.getResource() for line in line_list)\n
try:\n
  resource, = resource_set\n
except ValueError:\n
  raise ValueError("%s doesn\'t have only one resource %s" % (\n
              context.getPath(), list(resource_set)))\n
if context.getResource() != resource:\n
  # set the resource on the transaction\n
  context.setResource(resource)\n
# and delete on the invoice lines, so that if the user changes\n
# the ressource on the transaction, it also change on the lines.\n
for line in line_list:\n
  line.setResource(None)\n
  assert line.getResource() == resource\n
\n
# round debit / credit on created transaction.\n
context.AccountingTransaction_roundDebitCredit()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>related_simulation_movement_path_list=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>InvoiceTransaction_postTransactionLineGeneration</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
