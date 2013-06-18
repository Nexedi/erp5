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
            <value> <string encoding="cdata"><![CDATA[

from Products.ERP5Type.Cache import CachingMethod\n
\n
def getAccountingPeriodStartDateForSectionCategory(section_category, date):\n
  portal = context.getPortalObject()\n
  # XXX for now we guess period start date from the first organisation having\n
  # accounting periods, giving priority to the organisation directly associated\n
  # to the section category\n
  section_uid = portal.Base_getSectionUidListForSectionCategory(\n
                                      section_category, strict_membership=True)\n
  section_uid.extend(portal.Base_getSectionUidListForSectionCategory(\n
                                      section_category, strict_membership=False))\n
  period_start_date = None\n
  for uid in section_uid:\n
    if uid == -1: continue # Base_getSectionUidListForSectionCategory returns [-1] if no section_uid exists \n
    section = portal.portal_catalog.getObject(uid)\n
    for ap in section.contentValues(portal_type=\'Accounting Period\',\n
                        checked_permission=\'Access contents information\'):\n
      if ap.getSimulationState() not in (\'planned\', \'confirmed\',\n
                                         \'started\', \'stopped\',\n
                                         \'closing\', \'delivered\'):\n
        continue\n
      if ap.getStartDate().earliestTime() <= date <= ap.getStopDate().latestTime():\n
        period_start_date = ap.getStartDate().earliestTime()\n
    if period_start_date:\n
      break\n
  else:\n
    period_start_date = DateTime(date.year(), 1, 1)\n
  return period_start_date\n
\n
getAccountingPeriodStartDateForSectionCategory = CachingMethod(\n
              getAccountingPeriodStartDateForSectionCategory,\n
              id=script.getId(), cache_factory=\'erp5_content_long\')\n
\n
return getAccountingPeriodStartDateForSectionCategory(section_category, date)\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>section_category, date</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getAccountingPeriodStartDateForSectionCategory</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
