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
            <value> <string>from Products.ERP5Form.Report import ReportSection\n
from Products.ERP5Type.DateUtils import getIntervalListBetweenDates\n
from DateTime import DateTime\n
result=[]\n
# civil status\n
result.append(ReportSection(\n
              path=context.getPhysicalPath(),\n
              title=context.Base_translateString(\'Civil Status\'),\n
              form_id=\'Person_viewPersonDetailedCivilStatus\'))\n
\n
# career list\n
result.append(ReportSection(\n
              path=context.getPhysicalPath(),\n
              title=context.Base_translateString(\'Careers\'),\n
              listbox_display_mode=\'FlatListMode\',\n
              form_id=\'Person_viewPersonDetailedCareerList\'))\n
\n
# event list only if event module exists\n
if context.getPortalObject().hasObject(\'event_module\'):\n
  result.append(ReportSection(\n
    path=context.getPhysicalPath(),\n
    title=context.Base_translateString(\'Events\'),\n
    listbox_display_mode=\'FlatListMode\',\n
    form_id=\'Person_viewPersonDetailedEventList\'))\n
\n
# contributions list\n
if context.getReference() not in (None, ""):\n
  # list only if user has a login defined\n
  aggregation_level = context.REQUEST.get(\'aggregation_level\')\n
  from_date = context.REQUEST.get(\'from_date\')\n
  to_date = context.REQUEST.get(\'at_date\')\n
\n
  selection_columns = [(\'document_type\', "Document Type")]\n
  if from_date is None:\n
    # get the minimum creation date in catalog\n
    select_expression = "MIN(creation_date)"\n
    group_by = "creation_date"\n
    from_date = DateTime(context.portal_catalog(select_expression=select_expression,\n
                                       group_by_expression=group_by,\n
                                       limit=1)[0][2])\n
  # get period list between given date\n
  interval_list_dict = getIntervalListBetweenDates(from_date=from_date, to_date=to_date,\n
                                              keys={\'year\':aggregation_level=="year",\n
                                                    \'month\':aggregation_level=="month",\n
                                                    \'week\' : aggregation_level=="week",\n
                                                    \'day\':aggregation_level=="day"})\n
  interval_list = interval_list_dict[aggregation_level]\n
  # list columns of the listbox\n
  selection_columns.extend([(x,x) for x in interval_list])\n
  selection_columns.append((\'total\', \'Total\'))\n
  params=dict(period_list=interval_list)\n
\n
  # stat columns of the listbox\n
  stat_columns = [(\'document_type\',\'document_type\'),]+[(x,x) for x in interval_list]+[(\'total\', \'total\'),]\n
  context.REQUEST.set(\'stat_columns\', stat_columns)\n
\n
  result.append(ReportSection(\n
                path=context.getPhysicalPath(),\n
                selection_columns=selection_columns,\n
                listbox_display_mode=\'FlatListMode\',\n
                title=context.Base_translateString(\'Contributions\'),\n
                selection_params=params,\n
                form_id=\'Person_viewPersonDetailedContributionList\'))\n
\n
\n
return result\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Person_getPersonDetailedReportSectionList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
