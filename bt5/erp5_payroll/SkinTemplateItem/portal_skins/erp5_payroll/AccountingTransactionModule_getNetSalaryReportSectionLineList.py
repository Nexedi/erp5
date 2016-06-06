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
            <value> <string>from Products.PythonScripts.standard import Object\n
from DateTime import DateTime\n
\n
request = context.REQUEST\n
portal = context.getPortalObject()\n
translateString = portal.Base_translateString\n
\n
net_salary_base_amount_uid = \\\n
              portal.portal_categories.base_amount.payroll.report.salary.net.getUid()\n
employee_contribution_share_uid = \\\n
              portal.portal_categories.contribution_share.employee.getUid()\n
\n
section_category = request[\'section_category\']\n
section_uid = portal.Base_getSectionUidListForSectionCategory(section_category)\n
\n
# currency precision\n
currency = portal.Base_getCurrencyForSection(section_category)\n
precision = portal.account_module.getQuantityPrecisionFromResource(currency)\n
request.set(\'precision\', precision)\n
\n
from_date = None\n
if request.get(\'from_date\'):\n
  from_date = DateTime(request[\'from_date\'])\n
at_date = DateTime(request[\'at_date\'])\n
simulation_state = request[\'simulation_state\']\n
\n
object_list = []\n
total_price = 0\n
\n
# FIXME: this report does not support multiple Payment Condition\n
for inventory in portal.portal_simulation.getInventoryList(\n
                    parent_base_contribution_uid=net_salary_base_amount_uid,\n
                    contribution_share_uid=employee_contribution_share_uid,\n
                    portal_type=(\'Pay Sheet Line\', \'Pay Sheet Cell\'),\n
                    section_uid=section_uid,\n
                    simulation_state=simulation_state,\n
                    precision=precision,\n
                    from_date=from_date,\n
                    at_date=at_date,\n
                    group_by_resource=0,\n
                    group_by_node=1, ):\n
  price = inventory.total_price or 0\n
  total_price += price\n
  movement = inventory.getObject()\n
  employee = movement.getDestinationValue()\n
  employee_bank_account = movement.getExplanationValue()\\\n
                                      .getDefaultPaymentConditionSourcePaymentTitle()\n
\n
  object_list.append(\n
      Object(uid=-1,\n
             employee_career_reference=employee.getCareerReference(),\n
             employee_title=employee.getTitle(),\n
             employee_bank_account=employee_bank_account,\n
             total_price=price))\n
\n
request.set(\'total_price\', total_price)\n
\n
def sort_method(a, b):\n
  employee_career_reference_diff = cmp(a.employee_career_reference,\n
                                       b.employee_career_reference)\n
  if employee_career_reference_diff:\n
    return employee_career_reference_diff\n
  return cmp(a.employee_title, b.employee_title)\n
\n
object_list.sort(sort_method)\n
\n
return object_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>AccountingTransactionModule_getNetSalaryReportSectionLineList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
