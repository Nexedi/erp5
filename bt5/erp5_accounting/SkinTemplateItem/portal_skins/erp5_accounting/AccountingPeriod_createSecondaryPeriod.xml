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

from DateTime import DateTime\n
from Products.ERP5Type.DateUtils import addToDate\n
from Products.ERP5Type.Message import translateString\n
\n
month_added = 1\n
if frequency == \'quarterly\':\n
  month_added = 3\n
\n
date = context.getStartDate()\n
while date < context.getStopDate():\n
  end_date = addToDate(date, dict(month=month_added))\n
  # recreate a DateTime to have it in the proper timezone\n
  start_date = DateTime(date.year(), date.month(), date.day())\n
  stop_date = DateTime((end_date - 1).year(),\n
                       (end_date - 1).month(),\n
                       (end_date - 1).day())\n
\n
  period = context.newContent(portal_type=\'Accounting Period\',\n
                              start_date=start_date,\n
                              stop_date=stop_date)\n
\n
  if frequency == \'quarterly\':\n
    period.setShortTitle(\'%s-%s\' % (\n
      start_date.strftime(\'%Y %m\'), (end_date - 1).strftime(\'%m\')))\n
  else:\n
    period.setShortTitle(start_date.strftime(\'%Y-%m\'))\n
    period.setTitle(str(translateString(start_date.strftime(\'%B\'))))\n
\n
  if open_periods:\n
    period.start()\n
\n
  date = end_date\n
  \n
return context.Base_redirect(form_id,\n
     keep_items=dict(portal_status_message=translateString(\'Accounting periods created.\')))\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>frequency, open_periods=0, form_id=\'view\'</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>AccountingPeriod_createSecondaryPeriod</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
