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
            <value> <string>\'\'\'\n
This script will call the PaySheetTransaction_getMovementTotalPriceFromCategory\n
script to get the year to date summed amount of paysheet lines wich category of\n
category_list parameter is in variation_category_list of the PaySheet line and \n
wich has a base_contribution in the base_contribution_list\n
\'\'\'\n
\n
portal = context.getPortalObject()\n
accounting_module = portal.accounting_module\n
\n
from_date=DateTime(context.getStartDate().year(), 1, 1)\n
to_date=context.getStartDate()\n
\n
search_params = {\n
    \'portal_type\'         : \'Pay Sheet Transaction\',\n
    \'delivery.start_date\' : {\'range\': "minmax", \'query\': (from_date, to_date)},\n
    \'delivery.source_section_uid\' : context.getSourceSectionUid(),\n
    \'delivery.destination_section_uid\' : context.getDestinationSectionUid(),\n
    \'simulation_state\'    : [\'confirmed\', \'stopped\', \'delivered\']\n
}\n
\n
paysheet_list = [r.getObject() for r in accounting_module.searchFolder(**search_params)]\n
paysheet_list.append(context)\n
\n
yearly_amount = 0.\n
\n
script_params = {\'base_contribution\': base_contribution,\n
                 \'contribution_share\': contribution_share,\n
                 \'no_base_contribution\': no_base_contribution,\n
                 \'include_empty_contribution\': include_empty_contribution,\n
                 \'excluded_reference_list\': excluded_reference_list}\n
\n
for paysheet in paysheet_list :\n
  monthly_amount = paysheet.PaySheetTransaction_getMovementTotalPriceFromCategory(**script_params)\n
  yearly_amount += monthly_amount\n
  \n
return yearly_amount * -1\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>base_contribution=None, contribution_share=None, no_base_contribution=False, include_empty_contribution=True, excluded_reference_list=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>PaySheetTransaction_getYearToDateMovementTotalPriceFromCategory</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
