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
  this script return the total price of the base contribution list\n
  from the first of january of the year of the paysheet and until\n
  the start_date of this current paysheet. Return 0.0 if there is no amount.\n
\'\'\'\n
\n
# XXX-Aurel : this script is currently not working as paysheet transaction line/cell\n
# are not in stock table due to the lack of source/destination definition\n
\n
if paysheet is None:\n
    paysheet = context\n
\n
# test the list parameters\n
if base_contribution_list is None:\n
  base_contribution_list = []\n
elif not (same_type(base_contribution_list, []) or\n
          same_type(base_contribution_list, ())):\n
  base_contribution_list = [base_contribution_list]\n
\n
portal = context.getPortalObject();\n
portal_simulation = portal.portal_simulation\n
\n
base_amount = portal.portal_categories.base_amount\n
\n
base_contribution_uid_list = []\n
for category in base_contribution_list:\n
  category_value = base_amount.restrictedTraverse(category)\n
  if category_value is None:\n
    raise ValueError, \'Category "%s/%s" not found.\' % (base_amount.getPath(), category)\n
  base_contribution_uid_list.append(category_value.getUid())\n
\n
params = {\n
    \'node_uid\' : paysheet.getSourceSectionUid(),\n
    \'mirror_section_uid\' : paysheet.getSourceSectionUid(),\n
    \'section_uid\' : paysheet.getDestinationSectionUid(),\n
    \'contribution_share_uid\' :\\\n
        portal.portal_categories.contribution_share.employee.getUid(),\n
    \'to_date\' : paysheet.getStartDate(),\n
    \'from_date\' : DateTime(paysheet.getStartDate().year(), 1, 1),\n
    \'simulation_state\'    : [\'stopped\', \'delivered\'],\n
    \'precision\' : paysheet.getPriceCurrencyValue().getQuantityPrecision(),\n
    \'parent_base_contribution_uid\' : base_contribution_uid_list,\n
    #\'src__\' : 1\n
  }\n
\n
return portal_simulation.getInventoryAssetPrice(**params)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>paysheet=None, base_contribution_list=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>PaySheetTransaction_getYearToDateBaseContributionTotalPrice</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
