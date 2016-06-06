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
            <value> <string># This script is called by each line of the domain in order to know if returned objects\n
#by the domain have the same property than returned objects\n
\n
object_domain = selection_report.asDomainItemDict()[\'project_report_monthly_domain\']\n
object_dict = context.object_dict\n
summary_dict = context.summary_dict\n
\n
current_criterion = object_domain.getCriterionList()\n
date = current_criterion[0].identity\n
result_list = []\n
if len(object_domain.getMembershipCriterionBaseCategoryList())==0:\n
  # First level, so level of month, we display summary of total\n
  # quantity per worker for the full month\n
  returned_object = summary_dict.get(date, None)\n
  if returned_object is not None:\n
    result_list.append(returned_object)\n
else:\n
  returned_object = object_dict.get(date, None)\n
  if returned_object is not None:\n
    # optimisation, in this report we have exactly one temp object at most\n
    # matching our domain, and we have already a dict with nice keys, so\n
    # there is no need to parse all temp objects\n
    membership_criterion_category_list = object_domain.getMembershipCriterionCategoryList()\n
    assert len(membership_criterion_category_list) == 1\n
    membership_criterion_category = membership_criterion_category_list[0]\n
    assert membership_criterion_category.startswith(\'source_project/\')\n
    project_relative_url = membership_criterion_category[len(\'source_project/\'):]\n
    if returned_object.has_key(project_relative_url):\n
      result_list.append(returned_object[project_relative_url])\n
return result_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>selection_report=None, selection=None, selection_domain=None, report_url=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Project_getMonthlyObjectList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
