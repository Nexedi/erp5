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

from Products.ERP5Type.DateUtils import atTheEndOfPeriod\n
request = container.REQUEST\n
from_date = request.get(\'from_date\', None)\n
to_date = request.get(\'at_date\', None)\n
aggregation_level = request.get(\'aggregation_level\', None)\n
if to_date is not None:\n
  to_date = atTheEndOfPeriod(to_date, period=aggregation_level)\n
career_list = []\n
if from_date is None and to_date is None:\n
  career_list = context.contentValues(filter={\'portal_type\':\'Career\'})\n
else:\n
  for career in context.contentValues(filter={\'portal_type\':\'Career\'}):\n
    if from_date is not None and to_date is not None:\n
      if career.getStartDate() >= from_date and career.getStartDate() < to_date \\\n
             or career.getStopDate() < to_date and career.getStopDate() >= from_date \\\n
             or career.getStartDate() < from_date and career.getStopDate() > to_date:\n
        career_list.append(career)\n
    elif from_date is not None:\n
      if career.getStartDate() >= from_date \\\n
             or career.getStopDate() >= from_date:\n
        career_list.append(career)\n
    elif to_date is not None:\n
      if career.getStartDate() < to_date \\\n
             or career.getStopDate() < to_date :\n
        career_list.append(career)\n
\n
def date_cmp(a, b):\n
  return cmp(a.getStartDate(), b.getStartDate())\n
\n
career_list.sort(date_cmp)\n
return career_list\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Person_getPersonDetailedCareerList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
