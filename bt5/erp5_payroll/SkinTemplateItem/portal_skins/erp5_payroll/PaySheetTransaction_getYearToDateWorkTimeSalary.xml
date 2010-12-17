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
            <value> <string>portal = context.getPortalObject()\n
accounting_module = portal.accounting_module\n
\n
from_date=DateTime(context.getStartDate().year(), 1, 1)\n
to_date=context.getStartDate()\n
\n
search_params = \\\n
  { \n
   \'portal_type\'         : \'Pay Sheet Transaction\',\n
   \'delivery.start_date\' : {\'range\': "minmax", \'query\': (from_date, to_date)},\n
   \'delivery.source_section_uid\' : context.getSourceSectionUid(),\n
   \'delivery.destination_section_uid\' : context.getDestinationSectionUid(),\n
   \'simulation_state\'    : [\'confirmed\', \'stopped\', \'delivered\'],\n
  }\n
\n
paysheet_list = accounting_module.searchFolder( **search_params)\n
\n
yearly_work_time = 0\n
for paysheet in paysheet_list:\n
  annotation_line = paysheet.getAnnotationLineFromReference(\\\n
      reference=\'work_time_annotation_line\')\n
  if annotation_line is None:\n
    annotation_line = getattr(paysheet, \'work_time_annotation_line\', None)\n
  if annotation_line is None:\n
    raise ValueError, "Paysheet %s has no Annotation Line with reference work_time_annotation_line"\\\n
                             % paysheet.getRelativeUrl()\n
  nb_heures = annotation_line.getQuantity()\n
  yearly_work_time += nb_heures\n
\n
return yearly_work_time\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>PaySheetTransaction_getYearToDateWorkTimeSalary</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
