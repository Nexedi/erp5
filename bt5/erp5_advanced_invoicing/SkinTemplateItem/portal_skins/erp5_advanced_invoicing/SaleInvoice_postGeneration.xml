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
            <value> <string>"""This script is called on the Invoice after the delivery builder has created\n
the new Invoice.\n
"""\n
from Products.ERP5Type.Message import translateString\n
\n
if related_simulation_movement_path_list is None:\n
  raise RuntimeError, \'related_simulation_movement_path_list is missing. Update ERP5 Product.\'\n
\n
invoice = context\n
\n
# set resource from price currency\n
#if not invoice.getResource():\n
#  invoice.setResource(invoice.getPriceCurrency())\n
\n
related_packing_list = invoice.getDefaultCausalityValue()\n
\n
# copy title, if not updating a new delivery\n
if not invoice.hasTitle() and related_packing_list.hasTitle():\n
  invoice.setTitle(related_packing_list.getTitle())\n
\n
# initialize accounting_workflow to confirmed state\n
if invoice.getSimulationState() == \'draft\':\n
  invoice.Delivery_confirm()\n
else:\n
  # call builder just same as after script of \'confirm\' transition\n
  invoice.localBuild()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>related_simulation_movement_path_list=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>SaleInvoice_postGeneration</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
